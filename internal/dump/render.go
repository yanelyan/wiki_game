package dump

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"os"

	"github.com/yanelyan/wiki_game/internal/graph"
	"github.com/yanelyan/wiki_game/internal/storage"
)

// LoadFromBin читает файл storage.SaveToBin в формате WGR1
// и возвращает graph.Graph, готовый для поиска пути.
// Порядок полей: Titles, TitleToID, Incoming, Outgoing.
// Длины имеют тип uint64, ID — uint32; все числа записаны в LittleEndian.
// Пустые и nil-коллекции в файле не различаются.
func LoadFromBin(path string) (*graph.Graph, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("открытие файла графа: %w", err)
	}
	defer f.Close()

	info, err := f.Stat()
	if err != nil {
		return nil, fmt.Errorf("получение размера файла графа: %w", err)
	}
	d := binDecoder{r: &io.LimitedReader{R: bufio.NewReader(f), N: info.Size()}}
	var header [4]byte
	if _, err := io.ReadFull(d.r, header[:]); err != nil {
		return nil, fmt.Errorf("чтение заголовка: %w", err)
	}
	if string(header[:]) != "WGR1" {
		return nil, fmt.Errorf("неизвестный формат графа: %q", header)
	}

	count, err := d.readLength(8) // У каждой строки есть длина uint64.
	if err != nil {
		return nil, fmt.Errorf("чтение числа названий: %w", err)
	}
	g := &storage.DataGraph{Titles: make([]string, count)}
	for i := range g.Titles {
		g.Titles[i], err = d.readString()
		if err != nil {
			return nil, fmt.Errorf("чтение названия %d: %w", i, err)
		}
	}

	count, err = d.readLength(12) // Длина строки uint64 и ID uint32.
	if err != nil {
		return nil, fmt.Errorf("чтение размера карты ID: %w", err)
	}
	g.TitleToID = make(map[string]uint32, count)
	for i := 0; i < count; i++ {
		title, err := d.readString()
		if err != nil {
			return nil, fmt.Errorf("чтение названия в карте ID: %w", err)
		}
		var id uint32
		if err := binary.Read(d.r, binary.LittleEndian, &id); err != nil {
			return nil, fmt.Errorf("чтение ID: %w", err)
		}
		if _, exists := g.TitleToID[title]; exists {
			return nil, fmt.Errorf("повторное название в карте ID: %q", title)
		}
		g.TitleToID[title] = id
	}

	g.Incoming, err = d.readNeighbors()
	if err != nil {
		return nil, fmt.Errorf("чтение входящих связей: %w", err)
	}
	g.Outgoing, err = d.readNeighbors()
	if err != nil {
		return nil, fmt.Errorf("чтение исходящих связей: %w", err)
	}
	if d.r.N != 0 {
		return nil, fmt.Errorf("лишние данные после графа: %d байт", d.r.N)
	}
	return graph.New(g.Titles, g.TitleToID, g.Incoming, g.Outgoing), nil
}

type binDecoder struct {
	r *io.LimitedReader
}

// Проверяем длину до выделения памяти: элементы должны помещаться в файле.
func (d *binDecoder) readLength(minBytes uint64) (int, error) {
	var length uint64
	if err := binary.Read(d.r, binary.LittleEndian, &length); err != nil {
		return 0, err
	}
	maxInt := uint64(^uint(0) >> 1)
	if length > maxInt || length > uint64(d.r.N)/minBytes {
		return 0, fmt.Errorf("недопустимая длина %d: осталось %d байт", length, d.r.N)
	}
	return int(length), nil
}

func (d *binDecoder) readString() (string, error) {
	length, err := d.readLength(1)
	if err != nil {
		return "", err
	}
	data := make([]byte, length)
	if _, err := io.ReadFull(d.r, data); err != nil {
		return "", err
	}
	return string(data), nil
}

func (d *binDecoder) readNeighbors() ([][]uint32, error) {
	count, err := d.readLength(8)
	if err != nil {
		return nil, err
	}
	neighbors := make([][]uint32, count)
	for i := range neighbors {
		length, err := d.readLength(4)
		if err != nil {
			return nil, fmt.Errorf("список %d: %w", i, err)
		}
		neighbors[i] = make([]uint32, length)
		if err := binary.Read(d.r, binary.LittleEndian, neighbors[i]); err != nil {
			return nil, fmt.Errorf("список %d: %w", i, err)
		}
	}
	return neighbors, nil
}

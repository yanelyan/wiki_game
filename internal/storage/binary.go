package storage

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"os"
)

type DataGraph struct {
	Titles    []string
	TitleToID map[string]uint32

	Incoming [][]uint32
	Outgoing [][]uint32
}

func SaveToBin(path string, graph *DataGraph) (err error) {
	if graph == nil {
		return fmt.Errorf("невозможно сохранить nil-граф")
	}

	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("создание файла графа: %w", err)
	}
	defer func() {
		if closeErr := f.Close(); closeErr != nil && err == nil {
			err = fmt.Errorf("закрытие файла графа: %w", closeErr)
		}
	}()

	w := bufio.NewWriter(f)
	order := binary.LittleEndian

	writeString := func(value string) error {
		if err := binary.Write(w, order, uint64(len(value))); err != nil {
			return err
		}
		_, err := w.WriteString(value)
		return err
	}
	writeNeighbors := func(neighbors [][]uint32) error {
		if err := binary.Write(w, order, uint64(len(neighbors))); err != nil {
			return err
		}
		for _, ids := range neighbors {
			if err := binary.Write(w, order, uint64(len(ids))); err != nil {
				return err
			}
			if err := binary.Write(w, order, ids); err != nil {
				return err
			}
		}
		return nil
	}

	if _, err := w.WriteString("WGR1"); err != nil {
		return fmt.Errorf("запись заголовка: %w", err)
	}
	if err := binary.Write(w, order, uint64(len(graph.Titles))); err != nil {
		return fmt.Errorf("запись числа названий: %w", err)
	}
	for _, title := range graph.Titles {
		if err := writeString(title); err != nil {
			return fmt.Errorf("запись названия: %w", err)
		}
	}
	if err := binary.Write(w, order, uint64(len(graph.TitleToID))); err != nil {
		return fmt.Errorf("запись размера карты ID: %w", err)
	}
	for title, id := range graph.TitleToID {
		if err := writeString(title); err != nil {
			return fmt.Errorf("запись названия в карте ID: %w", err)
		}
		if err := binary.Write(w, order, id); err != nil {
			return fmt.Errorf("запись ID: %w", err)
		}
	}
	if err := writeNeighbors(graph.Incoming); err != nil {
		return fmt.Errorf("запись входящих связей: %w", err)
	}
	if err := writeNeighbors(graph.Outgoing); err != nil {
		return fmt.Errorf("запись исходящих связей: %w", err)
	}
	if err := w.Flush(); err != nil {
		return fmt.Errorf("сброс буфера в файл: %w", err)
	}

	return nil
}

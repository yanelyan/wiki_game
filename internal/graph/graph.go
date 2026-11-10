package graph

import "errors"

type Graph struct {
	Titles    []string
	TitleToID map[string]uint32

	incoming [][]uint32
	outgoing [][]uint32
}

var ErrGraphNotExist = errors.New("graph does not exist")

// New создаёт граф с входящими и исходящими связями.
// Срезы и карта используются без копирования: после создания графа
// вызывающий код не должен изменять переданные данные.
func New(titles []string, titleToID map[string]uint32, incoming, outgoing [][]uint32) *Graph {
	return &Graph{
		Titles:    titles,
		TitleToID: titleToID,
		incoming:  incoming,
		outgoing:  outgoing,
	}
}

func (g *Graph) size() int {
	return len(g.Titles)
}

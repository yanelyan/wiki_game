package graph

import "errors"

type Graph struct {
	Titles []string 
	TitleToID map[string]uint32 

	incoming [][]uint32
	outgoing [][]uint32
}

var ErrGraphNotExist = errors.New("graph does not exist")

func (g *Graph) OutNeighbors(v uint32) ([]uint32, error) {
	if g == nil {
		return nil, ErrGraphNotExist
	}
	return g.outgoing[v], nil
}

func (g *Graph) InNeighbors(v uint32) ([]uint32, error) {
	if g == nil {
		return nil, ErrGraphNotExist
	}
	return g.incoming[v], nil
}


func (g *Graph) size() int{
	return len(g.Titles)
}
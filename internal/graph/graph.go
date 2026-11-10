package graph

import "errors"

type Graph struct {
	Titles []string 
	TitleToID map[string]uint32 

	incoming [][]uint32
	outgoing [][]uint32
}

var ErrGraphNotExist = errors.New("graph does not exist")


func (g *Graph) size() int{
	return len(g.Titles)
}
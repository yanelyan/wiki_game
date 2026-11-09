package graph

type Graph struct {
	Titles []string

	incoming [][]uint32
	outgoing [][]uint32
}

func (g *Graph) OutNeighbors(v uint32) []uint32 {
	return g.outgoing[v]
}

func (g *Graph) InNeighbors(v uint32) []uint32 {
	return g.incoming[v]
}

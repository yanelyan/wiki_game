package graphs

import (
	"fmt"
	"slices"
)

func FindPath(graph *Graph, start, end string) ([]string, error) {
	if graph == nil {
		return nil, ErrGraphNotExist
	}

	startID, ok := graph.TitleToID[start]
	if !ok {
		return nil, fmt.Errorf("статья %q не найдена", start)
	}
	endID, ok := graph.TitleToID[end]
	if !ok {
		return nil, fmt.Errorf("статья %q не найдена", end)
	}
	visitedFromStart := make([]bool, graph.size())
	visitedFromEnd := make([]bool, graph.size())
	parentFromStart := make([]uint32, graph.size())
	parentFromEnd := make([]uint32, graph.size())

	visitedFromStart[startID] = true
	visitedFromEnd[endID] = true
	frontFromStart := []uint32{uint32(startID)}
	frontFromEnd := []uint32{uint32(endID)}

	expand := func(front []uint32, neighbors [][]uint32, visited, otherVisited []bool, parent []uint32) ([]uint32, int) {
		var next []uint32
		for _, vertex := range front {
			for _, neighbor := range neighbors[vertex] {
				if visited[neighbor] {
					continue
				}
				visited[neighbor] = true
				parent[neighbor] = vertex
				if otherVisited[neighbor] {
					return nil, int(neighbor)
				}
				next = append(next, neighbor)
			}
		}
		return next, -1
	}

	for len(frontFromStart) > 0 && len(frontFromEnd) > 0 {
		var meeting int
		if len(frontFromStart) <= len(frontFromEnd) {
			frontFromStart, meeting = expand(frontFromStart, graph.outgoing, visitedFromStart, visitedFromEnd, parentFromStart)
		} else {
			frontFromEnd, meeting = expand(frontFromEnd, graph.incoming, visitedFromEnd, visitedFromStart, parentFromEnd)
		}
		if meeting == -1 {
			continue
		}

		path := make([]string, 0)
		for vertex := uint32(meeting); vertex != uint32(startID); vertex = parentFromStart[vertex] {
			path = append(path, graph.Titles[vertex])
		}
		path = append(path, start)
		slices.Reverse(path)

		for vertex := uint32(meeting); vertex != uint32(endID); {
			vertex = parentFromEnd[vertex]
			path = append(path, graph.Titles[vertex])
		}
		return path, nil
	}

	return nil, fmt.Errorf("path not found")
}

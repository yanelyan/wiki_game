package main

import (
	"fmt"
	"github.com/yanelyan/wiki_game/internal/dump"
	"github.com/yanelyan/wiki_game/internal/graphs"
	"strings"
)

func main() {
	graph_from_json, err := dump.LoadFromBin("graphs/generated/test.bin")
	if err != nil {
		panic(err)
	}

	var start, end = "Старт", "Финиш"

	wiki_path, err := graphs.FindPath(graph_from_json, start, end)
	if err != nil {
		panic(err)
	}

	fmt.Println(strings.Join(wiki_path, " → "))

}

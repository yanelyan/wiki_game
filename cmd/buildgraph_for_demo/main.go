package main

import "github.com/yanelyan/wiki_game/internal/storage"

func main() {
	err := storage.BuildTestGraph()
	if err != nil {
		panic(err)
	}

}

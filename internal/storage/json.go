package storage

import (
	"encoding/json"
	"fmt"
	"os"
)

func BuildTestGraph() error {
	data, err := os.ReadFile("graphs/test.json")
	if err != nil {
		return fmt.Errorf("ошибка с открытием файла %w", err)
	}

	var g DataGraph
	err = json.Unmarshal(data, &g)
	if err != nil {
		return fmt.Errorf("ошибка с преобразование json %w", err)
	}

	g.TitleToID = make(map[string]uint32, len(g.Titles))
	for i, v := range g.Titles {
		g.TitleToID[v] = uint32(i)
	}

	err = SaveToBin("graphs/generated/test.bin", &g)
	if err != nil {
		return fmt.Errorf("ошибка сохранения в bin файл %w", err)
	}

	return nil
}

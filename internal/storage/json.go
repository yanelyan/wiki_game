package storage

import (
	"encoding/json"
	"fmt"
	"os"
)





func BuildTestGraph() error{
	data, err := os.ReadFile("wiki_game/graphs/test.json")
	if err != nil{
		return fmt.Errorf("ошибка с открытием файла %w", err)	
	}
	

	var g DataGraph
	err = json.Unmarshal(data, &g)
	if err != nil{
		return fmt.Errorf("ошибка с преобразование json %w", err)
	}

	//TODO вызов функции из binary.go, для преобразования в .bin



	return nil
}

package storage



type DataGraph struct {
	Titles []string
	TitleToID map[string]uint32 

	incoming [][]uint32
	outgoing [][]uint32
}

// TODO уневерсальное преобразование из DataGraph в .bin 
package storage



type DataGraph struct{
	Titles []string

	Incoming [][]uint32
	Outgoing [][]uint32
}

// TODO уневерсальное преобразование из DataGraph в .bin 
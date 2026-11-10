package dump

import (
	"bytes"
	"encoding/hex"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/yanelyan/wiki_game/internal/storage"
)

func TestLoadFromBinRoundTrip(t *testing.T) {
	want := &storage.DataGraph{
		Titles:    []string{"Старт", "Финиш", "Остров"},
		TitleToID: map[string]uint32{"Старт": 0, "Финиш": 1, "Остров": 2},
		Incoming:  [][]uint32{{}, {0, 1}, {}},
		Outgoing:  [][]uint32{{1}, {1}, {}},
	}
	path := filepath.Join(t.TempDir(), "graph.bin")
	if err := storage.SaveToBin(path, want); err != nil {
		t.Fatal(err)
	}
	got, err := LoadFromBin(path)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %+v, want %+v", got, want)
	}
}

func TestLoadFromBinFixture(t *testing.T) {
	// Independent fixture checks byte lengths for UTF-8 and a multi-byte ID.
	data, err := hex.DecodeString("57475231" +
		"01000000000000000200000000000000d0af" +
		"01000000000000000200000000000000d0af78563412" +
		"01000000000000000000000000000000" +
		"0100000000000000010000000000000078563412")
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(t.TempDir(), "graph.bin")
	if err := os.WriteFile(path, data, 0600); err != nil {
		t.Fatal(err)
	}
	got, err := LoadFromBin(path)
	if err != nil {
		t.Fatal(err)
	}
	want := &storage.DataGraph{
		Titles: []string{"Я"}, TitleToID: map[string]uint32{"Я": 0x12345678},
		Incoming: [][]uint32{{}}, Outgoing: [][]uint32{{0x12345678}},
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %+v, want %+v", got, want)
	}

	// Every truncated prefix must fail without returning a partial graph.
	for i := 0; i < len(data); i++ {
		if err := os.WriteFile(path, data[:i], 0600); err != nil {
			t.Fatal(err)
		}
		if g, err := LoadFromBin(path); err == nil || g != nil {
			t.Fatalf("accepted truncated file of %d bytes: graph=%+v, error=%v", i, g, err)
		}
	}

	badHeader := bytes.Clone(data)
	badHeader[3] = '2'
	badLength := bytes.Clone(data)
	copy(badLength[4:12], bytes.Repeat([]byte{0xff}, 8))
	badStringLength := bytes.Clone(data)
	copy(badStringLength[12:20], bytes.Repeat([]byte{0xff}, 8))
	for name, invalid := range map[string][]byte{
		"version": badHeader, "count": badLength, "string length": badStringLength,
		"trailing bytes": append(bytes.Clone(data), 0),
	} {
		t.Run(name, func(t *testing.T) {
			if err := os.WriteFile(path, invalid, 0600); err != nil {
				t.Fatal(err)
			}
			if g, err := LoadFromBin(path); err == nil || g != nil {
				t.Fatalf("accepted invalid file: graph=%+v, error=%v", g, err)
			}
		})
	}
}

func TestLoadFromBinEmptyGraph(t *testing.T) {
	path := filepath.Join(t.TempDir(), "empty.bin")
	if err := storage.SaveToBin(path, &storage.DataGraph{}); err != nil {
		t.Fatal(err)
	}
	g, err := LoadFromBin(path)
	if err != nil {
		t.Fatal(err)
	}
	if len(g.Titles)+len(g.TitleToID)+len(g.Incoming)+len(g.Outgoing) != 0 {
		t.Fatalf("expected an empty graph, got %+v", g)
	}
}

func TestLoadFromBinMissingFile(t *testing.T) {
	if g, err := LoadFromBin(filepath.Join(t.TempDir(), "missing.bin")); err == nil || g != nil {
		t.Fatalf("expected an open error, got graph=%+v, error=%v", g, err)
	}
}

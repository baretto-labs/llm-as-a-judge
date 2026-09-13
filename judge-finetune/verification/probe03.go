package main

// Probes for batch_03 Go examples: slice aliasing on append, and a worker pool.

import (
	"fmt"
	"sort"
	"sync"
)

// b03-005 candidate: filter that reuses the caller's backing array
func filterInPlace(nums []int) []int {
	out := nums[:0]
	for _, n := range nums {
		if n%2 == 0 {
			out = append(out, n)
		}
	}
	return out
}

func filterCopy(nums []int) []int {
	out := make([]int, 0, len(nums))
	for _, n := range nums {
		if n%2 == 0 {
			out = append(out, n)
		}
	}
	return out
}

// b03-004 candidate: bounded worker pool
func squareAll(nums []int, workers int) []int {
	jobs := make(chan int)
	results := make(chan int)
	var wg sync.WaitGroup

	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for n := range jobs {
				results <- n * n
			}
		}()
	}
	go func() {
		for _, n := range nums {
			jobs <- n
		}
		close(jobs)
	}()
	go func() {
		wg.Wait()
		close(results)
	}()

	out := make([]int, 0, len(nums))
	for r := range results {
		out = append(out, r)
	}
	sort.Ints(out)
	return out
}

func main() {
	original := []int{1, 2, 3, 4, 5, 6}
	kept := filterInPlace(original)
	fmt.Println("b03-005 filterInPlace -> résultat :", kept)
	fmt.Println("b03-005 slice d'origine après appel :", original)

	original2 := []int{1, 2, 3, 4, 5, 6}
	kept2 := filterCopy(original2)
	fmt.Println("b03-005 filterCopy   -> résultat :", kept2)
	fmt.Println("b03-005 slice d'origine après appel :", original2)

	fmt.Println("b03-004 squareAll([1..6], 3) :", squareAll([]int{1, 2, 3, 4, 5, 6}, 3))
}

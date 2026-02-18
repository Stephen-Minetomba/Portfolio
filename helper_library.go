package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Input/Output or I/O
func sayNl(a ...interface{}) {
	fmt.Print(a...)
}
func say(a ...interface{}) {
	fmt.Println(a...)
}
func input(prompt string) string {
	var userInput string
	sayNl(prompt)
	reader := bufio.NewReader(os.Stdin)
	userInput, _ = reader.ReadString('\n')
	return strings.TrimSpace(userInput)
}

// String manipulation
func lowercase(inp string) string {
	lower := strings.ToLower(inp)
	return lower
}
func uppercase(inp string) string {
	upper := strings.ToUpper(inp)
	return upper
}

// List stuff
// Append is done like this:
// list1 := placeholder_list
// list2 := placeholder_list
// list1 = append(list1, list2...) // Notice the ..., this is what you must do if you add two slices. If you simply want to add a value to a list, then don't use the ...
func split(s string, delimeter string) []string {
	return strings.Split(s, delimeter)
}
func join[T any](list []T) string {
	result := ""
	for i, v := range list {
		if i > 0 {
			result += ", "
		}
		result += fmt.Sprint(v)
	}
	return result
}
func lengthString(s string) int {
	return len(s)
}
func lengthList[T any](l []T) int {
	return len(l)
}
func sumFloat(list []float64) float64 {
	sum := 0.0
	for i := 0; i < lengthList(list); i++ {
		sum += list[i]
	}
	return sum
}
func sumInt(list []int) int {
	sum := 0
	for i := 0; i < lengthList(list); i++ {
		sum += list[i]
	}
	return sum
}
func occurences(text string, list []string) int {
	count := 0
	for _, item := range list {
		if text == item {
			count += 1
		}
	}
	return count
}
func findLargestInt(numbers []int) int {
	if len(numbers) == 0 {
		return 0
	}
	largest := numbers[0]
	for _, num := range numbers {
		if num > largest {
			largest = num
		}
	}
	return largest
}
func findLargestFloat(numbers []float64) float64 {
	if len(numbers) == 0 {
		return 0.0
	}
	largest := numbers[0]
	for _, num := range numbers {
		if num > largest {
			largest = num
		}
	}
	return largest
}
func reverseString(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}
func reverseList[T any](list []T) []T {
	for i, j := 0, len(list)-1; i < j; i, j = i+1, j-1 {
		list[i], list[j] = list[j], list[i]
	}
	return list
}
func findSmallestInt(numbers []int) int {
	if len(numbers) == 0 {
		return 0
	}
	smallest := numbers[0]
	for _, num := range numbers {
		if num < smallest {
			smallest = num
		}
	}
	return smallest
}
func findSmallestFloat(numbers []float64) float64 {
	if len(numbers) == 0 {
		return 0.0
	}
	smallest := numbers[0]
	for _, num := range numbers {
		if num < smallest {
			smallest = num
		}
	}
	return smallest
}

// String conversions
func strToInt(s string) int {
	i, err := strconv.Atoi(s)
	if err != nil {
		fmt.Println("Error converting string to int:", err)
		return 0
	}
	return i
}
func intToStr(i int) string {
	s := strconv.Itoa(i)
	return s
}
func byteToStr(b byte) string {
	return string(b)
}
func runeToStr(r rune) string {
	return string(r)
}
func runeOrByteToStr(char interface{}) string {
	switch v := char.(type) {
	case byte:
		return byteToStr(v)
	case rune:
		return runeToStr(v)
	default:
		return ""
	}
}
func convertToStringNoMatterWhat[T any](val T) string {
	return fmt.Sprint(val)
}

// Mathematical
func isPrime(n int) bool {
	if n <= 1 {
		return false
	}
	for i := 2; i < n; i++ {
		if n%i == 0 {
			return false
		}
	}
	return true
}

func main() {
}

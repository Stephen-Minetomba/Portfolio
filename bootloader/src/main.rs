// ==================== CONSTRAINTS ====================
#![no_std]
#![no_main]

// ==================== IMPORTS ====================
extern crate alloc;

use uefi::data_types::chars::CharConversionError;
use uefi::prelude::*;
use uefi::proto::console::text::Key;
use core::fmt::Write;
use uefi::Char16;
use alloc::boxed::Box;
// ==================== HELPER FUNCTIONS ====================
fn char_to_char16(text: char) -> Option<Char16> {match Char16::try_from(text) {Ok(char16) => return Some(char16), Err(_error) => return None}}
fn char_to_key(text: char) -> Option<Key> {return char_to_char16(text).map(|c| Key::Printable(c))}

// ==================== MACROS ====================
macro_rules! wait {($system_table:expr, $microseconds:expr) => {$system_table.boot_services().stall($microseconds)};}
macro_rules! clear {($system_table:expr) => {$system_table.stdout().clear()};}
macro_rules! output {($system_table:expr, $text:expr) => {$system_table.stdout().write_str($text)};}
macro_rules! input {($system_table:expr) => {$system_table.stdin().read_key().ok().flatten()};}
macro_rules! is_pressed {($system_table:expr, $key:expr) => {$system_table.stdin().read_key().ok().flatten() == char_to_key($key)};}

// ==================== MEMORY ====================
struct Node<T> {value: T,next: Option<Box<Node<T>>>,}
pub struct LinkedList<T> {head: Option<Box<Node<T>>>,length: usize,}
impl<T> LinkedList<T> {
    pub fn new() -> Self {LinkedList {head: None,length: 0,}}
    pub fn push_front(&mut self, value: T) {let new_node = Box::new(Node {value,next: self.head.take(),});self.head = Some(new_node);self.length += 1;}
    pub fn pop_front(&mut self) -> Option<T> {self.head.take().map(|node| {self.head = node.next;self.length -= 1;node.value})}
    pub fn len(&self) -> usize {self.length}
    pub fn is_empty(&self) -> bool {self.head.is_none()}
    pub fn peek_front(&self) -> Option<&T> {self.head.as_ref().map(|node| &node.value)}
    pub fn peek_front_mut(&mut self) -> Option<&mut T> {self.head.as_mut().map(|node| &mut node.value)}
}

// ==================== KERNEL ====================
fn kernel(system_table: &mut SystemTable<Boot>) -> Status {
    let mut memory = LinkedList::new();
    loop {
        let _ = clear!(system_table);
        let _ = output!(system_table, "====================\r\n THE SUBLEQH KERNEL\r\n====================");
        let _ = output!(system_table, "- The first ever practical subleq interpreter, has hooks for filesystem + hardware + network access + I/O.\r\n");
        let _ = output!(system_table, "- SUBLEQH is a combination of 'Subleq' and 'H' where 'H' means 'Hooks'.\r\n");
        let _ = output!(system_table, "Possible inputs include:\r\n0\r\n1\r\n2\r\n3\r\n4\r\n5\r\n6\r\n7\r\n8\r\n9\r\nQ to quit\r\nH for separator\r\nB for deletion of the previous character\r\n");
        output!(system_table, "--------------------\r\n");
        output!(system_table, "Start holding.\r\n");
        wait!(system_table, 3_000_000);
        output!(system_table, "Receiving input...\r\n");
        system_table.stdin().wait_for_key_event();
        if is_pressed!(system_table, '0') {let _ = output!(system_table, "Inputted 0.\r\n");memory.push_front('0');}
        else if is_pressed!(system_table, '1') {let _ = output!(system_table, "Inputted 1.\r\n");memory.push_front('1');}
        else if is_pressed!(system_table, '2') {let _ = output!(system_table, "Inputted 2.\r\n");memory.push_front('2');}
        else if is_pressed!(system_table, '3') {let _ = output!(system_table, "Inputted 3.\r\n");memory.push_front('3');}
        else if is_pressed!(system_table, '4') {let _ = output!(system_table, "Inputted 4.\r\n");memory.push_front('4');}
        else if is_pressed!(system_table, '5') {let _ = output!(system_table, "Inputted 5.\r\n");memory.push_front('5');}
        else if is_pressed!(system_table, '6') {let _ = output!(system_table, "Inputted 6.\r\n");memory.push_front('6');}
        else if is_pressed!(system_table, '7') {let _ = output!(system_table, "Inputted 7.\r\n");memory.push_front('7');}
        else if is_pressed!(system_table, '8') {let _ = output!(system_table, "Inputted 8.\r\n");memory.push_front('8');}
        else if is_pressed!(system_table, '9') {let _ = output!(system_table, "Inputted 9.\r\n");memory.push_front('9');}
        else if is_pressed!(system_table, 'h') {let _ = output!(system_table, "Inputted a separator character.\r\n");memory.push_front(' ');}
        else if is_pressed!(system_table, 'q') {let _ = output!(system_table, "Quitting...\r\n");break;}
        else if is_pressed!(system_table, 'b') {let _ = output!(system_table, "Deleting...\r\n");memory.pop_front();}
        else {output!(system_table, "No input received.\r\n");}
        output!(system_table, "Input read.\r\n");
        wait!(system_table, 1_000_000);
        output!(system_table, "Stop holding.\r\n");
        wait!(system_table, 1_000_000);
    }
    // ==================== EXECUTION OF CODE ====================
    // To-Do: (I'm sorry that my code looks like garbage. I'll add more comments in later projects)
    // 1. The list must be reversed
    // 2. Do peek_front and pop_front repeateadly until the list is 0 (which you can do with a 'while' loop where you use the 'not_zero' function of the memory as the condition). Then, you can execute it. But in subleq you have to take 3, so just make another list repeateadly and use it to store the 3 values and run the program.
    // 3. Make a proper typing system

    let _ = output!(system_table, "shutting down...");
    wait!(system_table, 1_000_000);
    Status::SUCCESS
}

// ==================== BOOTLOADER ====================
#[entry]fn efi_main(handle: Handle, mut system_table: SystemTable<Boot>) -> Status {uefi_services::init(&mut system_table).unwrap(); kernel(&mut system_table)}

// Do not put a panic handler or else the compiler will give a compiling error. The UEFI library already gives it.

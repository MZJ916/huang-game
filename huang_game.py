import tkinter as tk
from tkinter import messagebox
import random

SIZE = 9


def is_valid(board, row, col, num):
    for c in range(SIZE):
        if board[row][c] == num:
            return False
    for r in range(SIZE):
        if board[r][col] == num:
            return False
    return True


def fill_board(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid(board, r, c, n):
                        board[r][c] = n
                        if fill_board(board):
                            return True
                        board[r][c] = 0
                return False
    return True


def generate_solution():
    board = [[0] * SIZE for _ in range(SIZE)]
    fill_board(board)
    return board


def generate_puzzle(solution, holes=45):
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)
    for r, c in cells[:holes]:
        puzzle[r][c] = 0
    return puzzle


class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("黄格格又菜又爱玩")
        self.root.configure(bg="#1e2a36")
        self.root.resizable(False, False)

        self.solution = None
        self.puzzle = None
        self.board = None
        self.fixed = None
        self.selected = (None, None)

        self._build_ui()
        self._new_game()

    def _build_ui(self):
        title = tk.Label(self.root, text="黄格格又菜又爱玩",
                         font=("Segoe UI", 20, "bold"),
                         fg="#dfeef9", bg="#1e2a36")
        title.pack(pady=(15, 8))

        board_frame = tk.Frame(self.root, bg="#0b141c", padx=10, pady=10)
        board_frame.pack(padx=25, pady=5)

        self.cells = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                btn = tk.Button(board_frame, width=3, height=1,
                                font=("Segoe UI", 18, "bold"),
                                relief="raised", bd=2,
                                command=lambda rr=r, cc=c: self._on_cell_click(rr, cc))
                btn.grid(row=r, column=c, padx=2, pady=2, ipadx=6, ipady=4)
                self.cells[r][c] = btn

        self.msg_var = tk.StringVar(value="点击格子开始")
        msg_label = tk.Label(self.root, textvariable=self.msg_var,
                             font=("Segoe UI", 12, "bold"),
                             fg="#d0e6f5", bg="#122430",
                             padx=12, pady=6, width=28)
        msg_label.pack(pady=10)

        num_frame = tk.Frame(self.root, bg="#1e2a36")
        num_frame.pack(pady=5)
        for i in range(1, 10):
            b = tk.Button(num_frame, text=str(i), width=3, height=1,
                          font=("Segoe UI", 16, "bold"),
                          bg="#f2f9ff", fg="#16384d",
                          command=lambda n=i: self._place_number(n))
            b.grid(row=0, column=i - 1, padx=3, pady=3, ipadx=4, ipady=2)

        btn_frame = tk.Frame(self.root, bg="#1e2a36")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="新游戏", width=8, font=("Segoe UI", 12, "bold"),
                  bg="#2e4c63", fg="white", command=self._new_game).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="清除", width=8, font=("Segoe UI", 12, "bold"),
                  bg="#2e4c63", fg="white", command=self._clear_cell).grid(row=0, column=1, padx=8)

    def _new_game(self):
        self.solution = generate_solution()
        self.puzzle = generate_puzzle(self.solution, holes=45)
        self.board = [row[:] for row in self.puzzle]
        self.fixed = [[self.puzzle[r][c] != 0 for c in range(SIZE)] for r in range(SIZE)]
        self.selected = (None, None)
        self.msg_var.set("点击格子开始")
        self._refresh_board()

    def _refresh_board(self):
        conflict = self._find_conflicts()
        for r in range(SIZE):
            for c in range(SIZE):
                val = self.board[r][c]
                text = str(val) if val != 0 else ""
                btn = self.cells[r][c]

                if (r, c) == self.selected:
                    bg, fg = "#ffc857", "#113246"
                elif (r, c) in conflict:
                    bg, fg = "#ffb3b3", "#7a0000"
                elif self.fixed[r][c]:
                    bg, fg = "#b9d2e7", "#0a2a3b"
                else:
                    bg, fg = "#eef4fa", "#113246"

                btn.config(text=text, bg=bg, fg=fg, activebackground=bg)

    def _find_conflicts(self):
        conflicts = set()
        for r in range(SIZE):
            seen = {}
            for c in range(SIZE):
                v = self.board[r][c]
                if v == 0:
                    continue
                if v in seen:
                    conflicts.add((r, c))
                    conflicts.add((r, seen[v]))
                else:
                    seen[v] = c
        for c in range(SIZE):
            seen = {}
            for r in range(SIZE):
                v = self.board[r][c]
                if v == 0:
                    continue
                if v in seen:
                    conflicts.add((r, c))
                    conflicts.add((seen[v], c))
                else:
                    seen[v] = r
        return conflicts

    def _is_complete(self):
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == 0:
                    return False
        return len(self._find_conflicts()) == 0

    def _on_cell_click(self, r, c):
        if self.fixed[r][c]:
            self.selected = (None, None)
            self.msg_var.set("固定格子不可编辑")
            self._refresh_board()
            return
        self.selected = (r, c)
        self.msg_var.set(f"选中 ({r + 1}, {c + 1})")
        self._refresh_board()

    def _place_number(self, n):
        r, c = self.selected
        if r is None:
            self.msg_var.set("请先点击一个空格子")
            return
        if self.fixed[r][c]:
            self.msg_var.set("固定格子不可修改")
            return
        self.board[r][c] = n
        self._refresh_board()
        if self._is_complete():
            # ★ 胜利提示已改
            self.msg_var.set("🎉 黄格格你真牛逼！")
            messagebox.showinfo("恭喜", "黄格格你真牛逼")
        else:
            if self._find_conflicts():
                self.msg_var.set("⚠️ 有重复数字，请调整")
            else:
                self.msg_var.set(f"已填入 {n}")

    def _clear_cell(self):
        r, c = self.selected
        if r is None:
            self.msg_var.set("请先选择一个格子")
            return
        if self.fixed[r][c]:
            self.msg_var.set("固定格子不能清除")
            return
        self.board[r][c] = 0
        self.msg_var.set("已清除")
        self._refresh_board()


if __name__ == "__main__":
    root = tk.Tk()
    SudokuGame(root)
    root.mainloop()

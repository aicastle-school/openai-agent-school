# from pathlib import Path
# from typing import Dict, Any, List

# MEMO_FILE = Path("test/memo.txt")

# def read_memo(with_lines: bool = False) -> Dict[str, Any]:
#     if not MEMO_FILE.exists():
#         return {"ok": True, "action": "read", "text": ""} if not with_lines else \
#                {"ok": True, "action": "read", "text": "", "lines": []}
#     lines = MEMO_FILE.read_text(encoding="utf-8").splitlines()
#     result = {"ok": True, "action": "read", "text": "\n".join(lines)}
#     if with_lines:
#         result["lines"] = [{"line": i + 1, "text": line} for i, line in enumerate(lines)]
#     return result

# def write_memo(content: str, mode: str = "overwrite", line_number: int | None = None) -> Dict[str, Any]:
#     mode = mode.lower()
#     if mode == "overwrite":
#         MEMO_FILE.write_text(content, encoding="utf-8")
#         return {"ok": True, "action": "overwrite", "text": content}
#     if mode == "append":
#         with MEMO_FILE.open("a", encoding="utf-8") as f:
#             f.write(content)
#         return {"ok": True, "action": "append", "content": content,
#                 "lines": read_memo(with_lines=True)["lines"]}
#     if mode == "insert":
#         lines: List[str] = []
#         if MEMO_FILE.exists():
#             lines = MEMO_FILE.read_text(encoding="utf-8").splitlines()
#         idx = max(0, min((line_number or len(lines)+1) - 1, len(lines)))
#         lines.insert(idx, content)
#         MEMO_FILE.write_text("\n".join(lines), encoding="utf-8")
#         return {"ok": True, "action": "insert", "inserted_line": line_number,
#                 "content": content, "lines": read_memo(with_lines=True)["lines"]}
#     return {"ok": False, "action": "write", "error": f"알 수 없는 mode: {mode}"}

# def delete_memo(line_numbers: List[int]) -> Dict[str, Any]:
#     """
#     여러 줄 삭제 (줄 번호 1부터). 예: [2, 4, 5]
#     - 중복은 자동 제거
#     - 범위를 벗어난 줄은 skipped로 반환
#     """
#     if not MEMO_FILE.exists():
#         return {"ok": False, "action": "delete", "error": "파일 없음"}

#     if not line_numbers:
#         return {"ok": False, "action": "delete", "error": "line_numbers가 비어 있습니다."}

#     lines = MEMO_FILE.read_text(encoding="utf-8").splitlines()
#     n = len(lines)

#     req_set = set(line_numbers)                    # 중복 제거
#     valid = sorted([ln for ln in req_set if 1 <= ln <= n], reverse=True)  # 뒤에서부터 삭제
#     skipped = sorted([ln for ln in req_set if ln < 1 or ln > n])
#     deleted_items = []

#     for ln in valid:
#         deleted_items.append({"line": ln, "text": lines[ln - 1]})
#         del lines[ln - 1]

#     MEMO_FILE.write_text("\n".join(lines), encoding="utf-8")

#     return {
#         "ok": True,
#         "action": "delete",
#         "requested_lines": sorted(req_set),
#         "deleted_lines": sorted([x["line"] for x in deleted_items]),
#         "deleted_items": sorted(deleted_items, key=lambda x: x["line"]),
#         "skipped_lines": skipped,
#         "lines": read_memo(with_lines=True)["lines"]
#     }

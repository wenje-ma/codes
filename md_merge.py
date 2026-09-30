from pathlib import Path
from tkinter import Tk,filedialog,messagebox
import re
def merge_markdown_files(selected_md_paths:list[str],output_md_path:str|None=None):
  if len(selected_md_paths)==0:
    raise ValueError("没有传入待合并的Markdown文件")
  first_file=Path(selected_md_paths[0])
  if output_md_path is None:
    out_file=first_file.parent/"document.md"
  else:
    out_file=Path(output_md_path)
  source_comment_pat=re.compile(r"\s*<!-- source file: .*? -->\r?\n?")
  with open(out_file,"w",encoding="utf-8") as out_f:
    for md_path_str in selected_md_paths:
      p=Path(md_path_str)
      print(f"正在合并: {p.name}")
      if not p.exists():
        print(f"⚠️跳过不存在文件: {p.name}")
        continue
      try:
        content=p.read_text(encoding="utf-8")
        content=source_comment_pat.sub("",content)
        out_f.write("\n\n")
        out_f.write(content)
      except Exception as e:
        print(f"⚠️读取失败跳过 {p.name}: {str(e)}")
  print(f"\n✅合并完成，输出文件: {out_file.resolve()}")
  return str(out_file)
def select_and_merge_md():
  root=Tk()
  root.withdraw()
  pick_files=messagebox.askyesno(
    title="选择处理对象",
    message="请选择要处理的对象类型：\n\n「是」→ 选择 Markdown 文件（可多选）\n「否」→ 选择文件夹（自动合并其中所有 .md）")
  if pick_files:
    selected_files=filedialog.askopenfilenames(title="请选择需要合并的 Markdown 文件（按住Ctrl多选，顺序就是合并顺序）",filetypes=[("Markdown 文件","*.md"),("All Files","*.*")])
    if not selected_files:
      print("未选择任何文件，程序退出。")
      return []
    merged_output=merge_markdown_files(list(selected_files))
    return [merged_output]
  folder=filedialog.askdirectory(title="请选择包含 Markdown 文件的文件夹")
  if not folder:
    print("未选择任何文件夹，程序退出。")
    return []
  md_files=sorted(Path(folder).rglob("*.md"))
  if not md_files:
    print(f"文件夹内未找到任何 .md 文件: {folder}")
    return []
  merged_output=merge_markdown_files([str(p) for p in md_files])
  return [merged_output]
if __name__=="__main__":
  select_and_merge_md()

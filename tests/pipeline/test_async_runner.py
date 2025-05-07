# from pathlib import Path
# from lovethedocs.application.pipeline import async_runner

# from tests.conftest import DummyUseCase, DummyFS

# def test_run_async_single_file(tmp_path, patch_progress, patch_summary):
#     dummy_mod = tmp_path/"demo.py"
#     dummy_mod.write_text("print('x')")
#     uc = DummyUseCase()
#     fs_factory = lambda root: DummyFS(root)

#     [fs] = async_runner.run_async(
#         paths=dummy_mod, concurrency=2,
#         fs_factory=fs_factory, use_case=uc
#     )

#     rel = Path("demo.py")
#     assert rel in fs.staged          # file was staged
#     # assert fs.staged[rel].endswith("# updated")
#     assert uc.calls                  # use_case was invoked

# def test_run_async_directory(tmp_path, patch_progress, patch_summary):
#     dir_ = tmp_path/"pkg"
#     dir_.mkdir()
#     (dir_/ "a.py").write_text("pass")
#     uc = DummyUseCase()
#     fs_factory = lambda root: DummyFS(root)

#     async_runner.run_async(
#         paths=[dir_], concurrency=1,
#         fs_factory=fs_factory, use_case=uc
#     )

#     # DummyFS.load_modules makes exactly one call per project
#     assert len(uc.calls) == 1
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import image_split


class SortingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def test_formats_case_and_nonrecursive_behavior(self):
        for name in ['canon.CR3', 'canon.cr2', 'sony.ARW', 'nikon.NEF', 'nikon.nrw',
                     'photo.JPG', 'photo.jpeg', 'notes.txt']:
            (self.folder / name).write_bytes(name.encode())
        nested = self.folder / 'nested'
        nested.mkdir()
        (nested / 'keep.jpg').write_bytes(b'nested')
        result = image_split.process_folder(self.folder)
        self.assertEqual(result, image_split.Result(raw=5, jpg=2, skipped=1))
        self.assertEqual((self.folder / 'raw/canon.CR3').read_bytes(), b'canon.CR3')
        self.assertTrue((nested / 'keep.jpg').exists())
        self.assertTrue((self.folder / 'notes.txt').exists())

    def test_collision_and_repeat_run(self):
        (self.folder / 'jpg').mkdir()
        (self.folder / 'jpg/photo.jpg').write_bytes(b'original')
        (self.folder / 'photo.jpg').write_bytes(b'new')
        image_split.process_folder(self.folder)
        self.assertEqual((self.folder / 'jpg/photo.jpg').read_bytes(), b'original')
        self.assertEqual((self.folder / 'jpg/photo_1.jpg').read_bytes(), b'new')
        self.assertEqual(image_split.process_folder(self.folder), image_split.Result())

    def test_symlinks_are_ignored_and_destination_links_rejected(self):
        (self.folder / 'notes.txt').write_bytes(b'keep')
        (self.folder / 'link.jpg').symlink_to(self.folder / 'notes.txt')
        self.assertEqual(image_split.process_folder(self.folder).jpg, 0)
        (self.folder / 'elsewhere').mkdir()
        (self.folder / 'jpg').symlink_to(self.folder / 'elsewhere', target_is_directory=True)
        (self.folder / 'photo.jpg').write_bytes(b'photo')
        with self.assertLogs('image_split', level='ERROR'):
            self.assertEqual(image_split.process_folder(self.folder).failed, 1)
        self.assertTrue((self.folder / 'photo.jpg').exists())
        self.assertEqual(list((self.folder / 'elsewhere').iterdir()), [])

    def test_failed_move_removes_reservation_and_preserves_source(self):
        src = self.folder / 'photo.jpg'
        src.write_bytes(b'image')
        with patch('image_split.shutil.move', side_effect=PermissionError('denied')):
            with self.assertLogs('image_split', level='ERROR'):
                self.assertEqual(image_split.process_folder(self.folder).failed, 1)
        self.assertEqual(src.read_bytes(), b'image')
        self.assertEqual(list((self.folder / 'jpg').iterdir()), [])

    def test_multiple_folders_and_invalid_folder_exit_status(self):
        other = self.folder / 'other folder'
        other.mkdir()
        (other / 'a.jpeg').write_bytes(b'a')
        with patch.object(image_split, 'LOG_PATH', self.folder / 'logs/run.log'):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertLogs('image_split', level='ERROR'):
                    status = image_split.main([str(other), str(self.folder / 'missing')])
        self.assertEqual(status, 1)
        self.assertEqual((other / 'jpg/a.jpeg').read_bytes(), b'a')

    def test_root_path_is_preserved(self):
        with patch('image_split.process_folder', return_value=image_split.Result()) as process:
            with patch.object(image_split, 'LOG_PATH', self.folder / 'run.log'):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(image_split.main(['/']), 0)
        process.assert_called_once_with('/')


if __name__ == '__main__':
    unittest.main()

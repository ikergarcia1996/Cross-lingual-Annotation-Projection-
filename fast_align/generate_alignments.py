from fast_align.utils import (
    data2fastalign,
    count_lines,
    run_bash_command,
    concatenate_files,
)
from fast_align.model_utils import align_corpus
import os
import argparse
from typing import List
import shutil
import uuid


def generate_word_alignments_fast_align(
    source_paths: List[str],
    target_paths: List[str],
    output_dir: str,
    output_names: List[str],
    source_parallel_corpus: List[str] = None,
    target_parallel_corpus: List[str] = None,
    tmp_dir: str = None,
    remove_tmp_dir: bool = True,
    fast_align_dir="fast_align/fast_align/build",
):
    if tmp_dir is None:
        tmp_dir = os.path.join(output_dir, f"tmp_dir_fastalign_{str(uuid.uuid4().hex)}")

    assert (
        len(source_paths) == len(target_paths) == len(output_names)
        and len(source_paths) > 0
    ), f"Number of source paths and target paths should be the same"
    assert (not source_parallel_corpus and not target_parallel_corpus) or (
        len(source_parallel_corpus) == len(target_parallel_corpus)
    ), f"Number of extra source paths and target paths should be the same"

    if not os.path.exists(os.path.dirname(output_dir)):
        os.makedirs(os.path.dirname(output_dir))

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    lines: List[int] = []

    for source_path, target_path in zip(source_paths, target_paths):
        source_lines: int = count_lines(source_path)
        target_lines: int = count_lines(target_path)
        assert source_lines == target_lines, (
            f"Number of lines in {source_path}: {source_lines}. "
            f"Number of lines in {target_path}: {target_lines}. "
        )

        lines.append(source_lines)
    if source_parallel_corpus and target_parallel_corpus:
        for source_path, target_path in zip(
            source_parallel_corpus, target_parallel_corpus
        ):
            source_lines: int = count_lines(source_path)
            target_lines: int = count_lines(target_path)
            assert source_lines == target_lines, (
                f"Number of lines in {source_path}: {source_lines}. "
                f"Number of lines in {target_path}: {target_lines}. "
            )

    source_train_path: str = os.path.join(tmp_dir, "source_sentences.txt")
    target_train_path: str = os.path.join(tmp_dir, "target_sentences.txt")

    source_files = source_paths
    if source_parallel_corpus is not None:
        source_files += source_parallel_corpus
    concatenate_files(input_paths=source_paths, output_path=source_train_path)

    target_files = target_paths
    if target_parallel_corpus is not None:
        target_files += target_parallel_corpus
    concatenate_files(input_paths=target_paths, output_path=target_train_path)

    print("Data 2 fast align format...")
    data2fastalign(
        source_path=source_train_path,
        target_path=target_train_path,
        output_path=os.path.join(tmp_dir, "dataset.fast_align"),
    )

    print("Running Fast Align...")

    align_corpus(
        fast_align_dir=fast_align_dir,
        corpus_path=os.path.join(tmp_dir, "dataset.fast_align"),
        output_dir=tmp_dir,
        alignment_direction="combine",
    )

    print("Retrieving alignments...")
    for direction_name in ["forward.talp", "reverse.talp", "grow_diag_final-and.talp"]:
        current_line: int = 1
        for file_len, file_name in zip(lines, output_names):
            output_name = os.path.join(output_dir, f"{file_name}.{direction_name}")
            command: str = (
                f"tail {os.path.join(tmp_dir,direction_name)} -n +{current_line} | head -n {file_len} > "
                f"{output_name}"
            )

            run_bash_command(command)

            current_line += file_len

    if remove_tmp_dir:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Alignments FastAlign")
    parser.add_argument(
        "--source_paths",
        type=str,
        required=True,
        nargs="+",
        help="Paths to the source sentences in txt format (one per line)",
    )

    parser.add_argument(
        "--target_paths",
        type=str,
        required=True,
        nargs="+",
        help="Paths to the target sentences in txt format (one per line)",
    )

    parser.add_argument(
        "--output_names",
        type=str,
        required=True,
        nargs="+",
        help="Names to the output files that we will store in the output_dir",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Path to were the alignment file is going to be stored",
    )

    parser.add_argument(
        "--source_parallel_corpus",
        type=str,
        required=False,
        nargs="+",
        help="Paths to the dataset augmentation corpus source sentences (one per line)",
    )

    parser.add_argument(
        "--target_parallel_corpus",
        type=str,
        required=False,
        nargs="+",
        help="Paths to the dataset augmentation corpus target sentences (one per line)",
    )

    args = parser.parse_args()

    generate_word_alignments_fast_align(
        source_paths=args.source_paths,
        target_paths=args.target_paths,
        source_parallel_corpus=args.source_parallel_corpus,
        target_parallel_corpus=args.target_parallel_corpus,
        output_names=args.output_names,
        output_dir=args.output_dir,
    )

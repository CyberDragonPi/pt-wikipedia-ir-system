import json
import os
import heapq


class SpimiMerger:
    def __init__(self, blocks_directory: str):
        self.blocks_directory = blocks_directory

    def merge_spimi_blocks_from_list(self):
        with open(self.blocks_directory, "r") as f:
            all_blocks = [line.strip().replace("\\", "/") for line in f if line.strip()]

        files = [open(p, "r", encoding="utf-8") for p in all_blocks]

        def read_next(f):
            line = f.readline()
            if not line:
                return None
            obj = json.loads(line)
            return next(iter(obj.items()))

        heap = []
        for idx, f in enumerate(files):
            pair = read_next(f)
            if pair:
                token, postings = pair
                heap.append((token, idx, postings))
        heapq.heapify(heap)

        final_index_path = os.path.join(self.output_directory, "final_index.json")
        with open(final_index_path, "w", encoding="utf-8") as out:
            out.write("{\n")
            first_token_written = False
            current_token = None
            current_postings = []

            write_buffer = []

            while heap:
                token, file_idx, postings = heapq.heappop(heap)

                if token == current_token:
                    current_postings.extend(postings)
                else:
                    if current_token is not None:
                        entry = f'{json.dumps(current_token)}: {json.dumps(current_postings)}'
                        write_buffer.append(entry)
                        if len(write_buffer) >= 100:
                            if first_token_written:
                                out.write(",\n")
                            out.write(",\n".join(write_buffer))
                            write_buffer.clear()
                            first_token_written = True

                        del current_postings

                    current_token = token
                    current_postings = postings

                next_pair = read_next(files[file_idx])
                if next_pair:
                    next_token, next_postings = next_pair
                    heapq.heappush(heap, (next_token, file_idx, next_postings))

            if current_token is not None:
                entry = f'{json.dumps(current_token)}: {json.dumps(current_postings)}'
                write_buffer.append(entry)

            if write_buffer:
                if first_token_written:
                    out.write(",\n")
                out.write(",\n".join(write_buffer))

            out.write("\n}")

        for f in files:
            f.close()

        self.delete_spimi_block_files()

    def delete_spimi_block_files(self):
        with open(self.block_paths_file, "r") as f:
            block_paths = [line.strip().replace("\\", "/") for line in f if line.strip()]

        for path in block_paths:
            if os.path.exists(path):
                os.remove(path)

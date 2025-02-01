#!/usr/bin/env python3
"""Parallel WARC file processor using multiprocessing."""

import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Optional
import os
import gzip

from warcio.archiveiterator import ArchiveIterator

from warc_record_parser import WarcRecordParser
from warc_record_processor_chain import WarcRecordProcessorChain
from processors.lexbor_html_processor import LexborHtmlProcessor
from plain_text_writer import PlainTextWriter
from models.warc_record import ProcessedWarcRecord


@dataclass
class ChunkInfo:
    """Information about a chunk of WARC records."""
    start_record: int
    record_count: int
    chunk_id: int


def get_file_chunks(input_path: str, num_chunks: int) -> List[ChunkInfo]:
    """Split WARC file into chunks based on record count.
    
    Args:
        input_path: Path to WARC file
        num_chunks: Number of chunks to split into
        
    Returns:
        List of chunk info with record ranges
    """
    # First pass: count total records
    total_records = 0

    with gzip.open(input_path, 'rb') as f:
        for record in ArchiveIterator(f):
            if record.rec_type == 'response':
                total_records += 1

    # Calculate records per chunk
    records_per_chunk = max(1, total_records // num_chunks)

    # Create chunks
    chunks = []
    current_chunk = 0

    for start_record in range(0, total_records, records_per_chunk):
        chunk_records = min(records_per_chunk, total_records - start_record)
        chunks.append(ChunkInfo(start_record, chunk_records, current_chunk))
        current_chunk += 1

    return chunks


def process_chunk(input_path: str, output_dir: str, chunk: ChunkInfo) -> None:  # pylint: disable=too-many-locals
    """Process a chunk of WARC records.
    
    Args:
        input_path: Path to WARC file
        output_dir: Directory for output files
        chunk: Chunk info with record ranges
    """
    # Create processor components
    record_parser = WarcRecordParser()
    html_processor = LexborHtmlProcessor()
    processors = [html_processor]
    processor_chain = WarcRecordProcessorChain(processors)
    output_writer = PlainTextWriter()

    # Configure output writer
    chunk_output = os.path.join(output_dir, f'chunk_{chunk.chunk_id}.txt')
    output_writer.configure(chunk_output)

    # Process records in chunk
    current_record = 0
    records_processed = 0

    with gzip.open(input_path, 'rb') as f:
        for record in ArchiveIterator(f):
            # Skip records until we reach our chunk
            if record.rec_type == 'response':
                if current_record < chunk.start_record:
                    current_record += 1
                    continue

                if records_processed >= chunk.record_count:
                    break

                try:
                    # Parse record
                    warc_record = record_parser.parse(record)
                    if not warc_record:
                        continue

                    # Process record
                    processed_content = processor_chain.process(warc_record)
                    if not processed_content:
                        continue

                    # Create processed record and write it
                    processed_record = ProcessedWarcRecord.from_record(
                        warc_record, processed_content)
                    output_writer.write_record(processed_record)
                    records_processed += 1

                except Exception as e:  # pylint: disable=broad-except
                    print(f"Error in chunk {chunk.chunk_id}: {str(e)[:80]}")
                    continue


def process_warc_parallel(input_path: str,
                          output_dir: str,
                          num_processes: Optional[int] = None) -> None:
    """Process WARC file in parallel using multiple processes.
    
    Args:
        input_path: Path to WARC file
        output_dir: Directory for output files
        num_processes: Number of processes to use, defaults to CPU count
    """
    if num_processes is None:
        num_processes = mp.cpu_count()

    print(f"Starting parallel processing with {num_processes} processes...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Split file into chunks
    chunks = get_file_chunks(input_path, num_processes)
    print(f"Split WARC file into {len(chunks)} chunks")

    # Create process pool
    with mp.Pool(processes=num_processes) as pool:
        # Process chunks in parallel
        jobs = []
        for chunk in chunks:
            job = pool.apply_async(process_chunk,
                                   (input_path, output_dir, chunk))
            jobs.append(job)

        # Wait for all jobs to complete
        for job in jobs:
            job.get()

    # Combine chunk outputs
    output_path = os.path.join(output_dir, 'combined_output.txt')
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for i in range(len(chunks)):
            chunk_path = os.path.join(output_dir, f'chunk_{i}.txt')
            if os.path.exists(chunk_path):
                with open(chunk_path, encoding='utf-8') as infile:
                    outfile.write(infile.read())
                os.remove(chunk_path)  # Clean up chunk file


if __name__ == '__main__':
    # Process the WARC file in parallel
    warc_file = ('/data01/commoncrawl/crawl-data/CC-NEWS/2024/12/'
                 'CC-NEWS-20241231224228-00155.warc.gz')
    output_directory = 'test_data/parallel_output'

    process_warc_parallel(warc_file, output_directory)
    print("Finished parallel processing")

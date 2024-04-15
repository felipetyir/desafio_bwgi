import io


def last_lines(file_path, max_read_size=io.DEFAULT_BUFFER_SIZE):
    with open(file_path, "rb") as file:
        list_of_read_elements = []

        while True:
            # Limiting the read amount to "max_read_size"
            text = file.read(max_read_size)

            # Checking whether the whole file has been read
            if not text:
                str_text = ''.join(list_of_read_elements)
                split_line = str_text.splitlines(True)

                list_of_lines = [line.replace('\r', '') if '\n' in line else line + '\n' for line in split_line]
                list_of_lines.reverse()

                result_iterator = iter(list_of_lines)
                break

            # Prevent from decoding incorrectly
            utf_8_decoded = text.decode("utf-8")
            list_of_read_elements.append(utf_8_decoded)

    return result_iterator


if __name__ == "__main__":
    last_lines = last_lines(r"my_file.txt")

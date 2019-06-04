from . import process_image


def get_picture():
    return process_image.take_picture()


def get_lock_state():
    filepath = "locked.jpg"
    process_image.take_picture(filepath)
    centers = process_image.run(filepath)

    # centers = process_image.run()

    if len(centers["orig"] == 1) and len(centers["blob"] == 2):
        pic_center = centers["orig"]
        blob_center = tuple()
        for pos in centers["blob"]:
            if not pos == pic_center:
                blob_center = pos

        return (blob_center - pic_center)
    else:
        return -1

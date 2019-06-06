from . import process_image


def get_picture():
    return process_image.take_picture()


def get_lock_state():
    filepath = "locked.jpg"
    # filepath = ''
    process_image.take_picture(filepath)
    centers = process_image.run(filepath)

    # centers = process_image.run()
    if (len(centers["orig"]) == 1) and (len(centers["blob"]) == 1):
        pic_center = centers["orig"][0]
        blob_center = tuple()
        for pos in centers["blob"]:
            if not (pos[1] == pic_center[1]):
                blob_center = pos

        return int((blob_center[1] - pic_center[1]) > 0)
    else:
        return -1

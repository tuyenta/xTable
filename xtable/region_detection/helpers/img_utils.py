def img_dim(img, bbox):
    """Get image dimension from bbox"""
    H_img, W_img, _ = img.shape
    x1_img, y1_img, x2_img, y2_img, _, _ = bbox
    w_table, h_table = x2_img - x1_img, y2_img - y1_img
    return [[x1_img, y1_img, x2_img, y2_img], [w_table, h_table], [H_img, W_img]]


def norm_bbox(img, bbox, x_corr=0.025, y_corr=0.025):
    """Add adition value for bbox results in x and y-axis
    In order to ensure the detected region can cover all the table, we will add an addition value for both x and y axis of the bbox
    Using the correlation value x_corr for x-axis and y_corr for y-axis

    Args:
        img (narray): image in array format
        x_corr (float): correlation value for x-axis. Default is 2.5%
        y_corr (float): correlation value for y-axis. Default is 2.5%
    Returns:
        (list): list of corrected coordinates, in form of [x0, y0, x1, y1]
        where (x0,y0) is the top-left, (x1, y1) is the bottom right.

    """
    [[x1_img, y1_img, x2_img, y2_img], [w_table, h_table], [H_img, W_img]] = img_dim(
        img, bbox
    )
    x1_img_norm, y1_img_norm, x2_img_norm, y2_img_norm = (
        x1_img / W_img,
        y1_img / H_img,
        x2_img / W_img,
        y2_img / H_img,
    )
    w_img_norm, h_img_norm = w_table / W_img, h_table / H_img
    w_corr = w_img_norm * x_corr
    h_corr = h_img_norm * y_corr

    return [
        x1_img_norm - w_corr,
        y1_img_norm - h_corr / 2,
        x2_img_norm + w_corr,
        y2_img_norm + h_corr / 2,
    ]


def bboxes_pdf(img, pdf_page, bbox):
    """Gets boundary of the table in pdf from the value in image

    Args:
        img (narray): Image in array
        pdf_page (object): pdf page
        bbox (narray): Boundary of the table in [x1, y1, x2, y2] format where (x1, y1) is bottom-left, (x2, y2) is top right
    Returns:
        (array): an array of value representing the cordinate of the table
    """

    W_pdf = float(pdf_page.cropBox.getLowerRight()[0])
    H_pdf = float(pdf_page.cropBox.getUpperLeft()[1])

    [x1_img_norm, y1_img_norm, x2_img_norm, y2_img_norm] = norm_bbox(img, bbox)
    x1, y1 = x1_img_norm * W_pdf, (1 - y1_img_norm) * H_pdf
    x2, y2 = x2_img_norm * W_pdf, (1 - y2_img_norm) * H_pdf

    return [max(x1, 0), min(y1, H_pdf), min(x2, W_pdf), max(y2, 0)]


def bboxes_img(img, pdf_page, bbox):
    """Gets boundary of the table in image from the value in pdf page

    Args:
        img (narray): Image in array
        pdf_page (object): pdf page
        bbox (narray): Boundary of the table in [x1, y1, x2, y2] format where (x1, y1) is bottom-left, (x2, y2) is top right
    Returns:
        (array): an array of value representing the cordinate of the table
    """

    W_pdf, H_pdf = float(pdf_page.cropBox.getLowerRight()[0]), float(
        pdf_page.cropBox.getUpperLeft()[1]
    )
    H_img, W_img, _ = img.shape

    x1, y1 = bbox[0] * (W_img / W_pdf), (1 - (bbox[3] / H_pdf)) * H_img
    x2, y2 = bbox[2] * (W_img / W_pdf), (1 - (bbox[1] / H_pdf)) * H_img

    return [x1, y1, x2, y2, None, None]

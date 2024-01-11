from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_order_robot_website()
    orders = get_orders()
    fill_form_and_submit_order(orders)
    archive_receipts()   

def open_order_robot_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number","Head","Body","Legs","Address"]
    )
    return orders

def fill_form_and_submit_order(orders):
    page = browser.page()

    for row in orders:
        page.select_option("#head",str(row["Head"]))
        page.set_checked("#id-body-"+str(row["Body"]), True)
        page.fill(".form-control",str(row["Legs"]))
        page.fill("#address",str(row["Address"]))
        page.click("#order")
        while (page.is_visible(".alert-danger")):
            page.click("#order")
        pdf_file = store_receipt_as_pdf(str(row["Order number"]))
        screenshot = screenshot_receipt(str(row["Order number"]))
        embed_screenshot_to_receipt(screenshot, pdf_file)

        page.wait_for_selector("#order-another")
        page.click("button:text('Order another robot')")
        page.click("button:text('OK')")    

def store_receipt_as_pdf(order_number):
    page = browser.page()
    store_receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(store_receipt_html, "output/store_receipt_{}.pdf".format(order_number))
    return "store_receipt_{}.pdf".format(order_number)

def screenshot_receipt(order_number):
    """Take a screenshot of the receipt"""
    page = browser.page()
    page.screenshot(path="output/receipt_{}.png".format(order_number))
    return "receipt_{}.png".format(order_number)  

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    list_of_files = [ 
        'output/{}'.format(pdf_file),
        'output/{}'.format(screenshot)
    ]
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document="output/final_docs/{}.pdf".format(str(pdf_file))
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output/final_docs', './output/final_docs.zip')
    
    






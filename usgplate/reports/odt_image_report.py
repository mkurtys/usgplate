import PIL.Image
from odf import table
from odf.draw import Frame, Image
from odf.opendocument import OpenDocumentText, load
from odf.style import (ParagraphProperties,
                       Style, TableCellProperties, TableColumnProperties,
                       TableProperties)
from odf.text import P
from odf.element import Text, Element

def get_image_info(filename):
    with PIL.Image.open(filename) as im:
        return im.size

def get_styles_from_doc(doc):
    styles = {}
    automaticstyles = {}
    for style in doc.styles.childNodes:
        if style.qname[1] == "style":
            styles[style.getAttribute("name")] = style

    for automaticstyle in doc.automaticstyles.childNodes:
        if automaticstyle.qname[1] == "style":
            automaticstyles[automaticstyle.getAttribute("name")] = automaticstyle
    
    return styles, automaticstyles

def get_last_element_from_doc(doc):
    text = doc.text
    last_element = text.childNodes[-1]
    return last_element

def append_style_or_replace(doc, doc_styles, style):
    if style.getAttribute("name") in doc_styles:
        doc.styles.removeChild(doc_styles[style.getAttribute("name")])
    
    doc.automaticstyles.addElement(style)
    doc_styles[style.getAttribute("name")] = style


def substitute_text(root, substitutions):
    for child in root.childNodes:
        if isinstance(child, Text): # getattr(child, "data", None):
            for key, value in substitutions.items():
                child.data = child.data.replace(key, value)
        else:
            substitute_text(child, substitutions)


def find_node_by_containing_text(root, text):
    for child in root.childNodes:
        if isinstance(child, Text):
            if text in child.data:
                return root
        else:
            found = find_node_by_containing_text(child, text)
            if found:
                return found
    return None

def find_parent_element_of_node(node):
    parent = node.parentNode
    if not parent:
        return None
    if isinstance(parent, Element):
        return parent
    else:
        return find_parent_element_of_node(parent)

def replace_node(node, new_node):
    parent = node.parentNode
    parent.insertBefore(new_node, node)
    parent.removeChild(node)

def create_odt_image_report(input_doc_filename: str | None,
                            picture_filenames: list[str],
                            image_size_real_cm: float = 6.0,
                            substitutions: dict[str, str] = {}):
    if not input_doc_filename:
        doc = OpenDocumentText()
    else:
        doc = load(input_doc_filename)

    substitute_text(doc.text, substitutions)

    align_center_style = Style(name="usgplate-align-center-style",
                              family="paragraph",
                              parentstylename="Table_20_Contents")
    align_center_style.addElement( ParagraphProperties(textalign="center") )

    table_style = Style(name="usgplate-table-style", family="table")
    table_style.addElement(TableProperties(width="17cm", align="margins",
                            backgroundcolor="transparent"))
    
    table_cell_style = Style(name="usgplate-table-cell-style", family="table-cell")
    table_cell_style.addElement(TableCellProperties(border=None, padding="0.1cm", verticalalign="middle", backgroundcolor="transparent"))
    
    picture_frame_style = Style(name="usgplate-picture-frame-style", family="graphic")

    styles, automaticstyles = get_styles_from_doc(doc)
    append_style_or_replace(doc, styles, align_center_style)
    append_style_or_replace(doc, styles, table_style)
    append_style_or_replace(doc, styles, table_cell_style)
    append_style_or_replace(doc, styles, picture_frame_style)


    columns_count = 2
    datatable = table.Table(name="image-table", stylename=table_style)
    datatable.addElement(table.TableColumn(stylename=TableColumnProperties(columnwidth="8cm"),
                                           numbercolumnsrepeated=columns_count))

    i=0
    table_row = None
    for picture_filename in picture_filenames:
        w, h = get_image_info(picture_filename)
        if w>h:
            w_cm = image_size_real_cm
            h_cm = image_size_real_cm * h / w
        else:
            w_cm = image_size_real_cm * w / h
            h_cm = image_size_real_cm
        x = i % columns_count
        y = i // columns_count

        if x == 0:
            table_row = table.TableRow()
            datatable.addElement(table_row)
        table_cell = table.TableCell(valuetype="string", stylename=table_cell_style)
        p = P(stylename=align_center_style)
        picture_frame = Frame(stylename=picture_frame_style,
                              anchortype="as-char",
                              width=f"{w_cm:.3f}cm",
                              height=f"{h_cm:.3f}cm"
                              )
        href = doc.addPicture(picture_filename)
        picture_frame.addElement(Image(href=href))
        p.addElement(picture_frame)
        table_cell.addElement(p)
        table_row.addElement(table_cell)

        i+=1
    
    insert_to = find_node_by_containing_text(doc.text, "$images")
    if insert_to is not None:
        replace_node(insert_to, datatable)
    else:
        doc.text.addElement(datatable)
    return doc
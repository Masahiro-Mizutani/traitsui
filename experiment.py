from pyface.qt import QtCore, QtGui
from traitsui.toolkit import toolkit


class MyBadWidget(QtGui.QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_disposed = []
        self.setText("Test")

    def sizeHint(self):
        if self.is_disposed:
            raise RuntimeError("Uhoh")
        return super().sizeHint()

    def event(self, event):
        print(self, event)
        return super().event(event)


class MyDialog(QtGui.QDialog):

    def closeEvent(self, event):
        print("Closing!")
        return super().closeEvent(event)

    def event(self, event):
        print(self, event)
        return super().event(event)


app = QtGui.QApplication([])


def create_widget(klass=MyDialog, n_widgets=3, parent=None):
    is_disposed = []
    main = klass(parent)
    layout = QtGui.QVBoxLayout()
    main.setLayout(layout)

    splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
    splitter.setStretchFactor(0, 2)
    layout.addWidget(splitter)

    widgets = [MyBadWidget() for _ in range(n_widgets)]
    for widget in widgets:
        splitter.addWidget(widget)
    return main, layout, widgets[-1] if widgets else None


STRUCTURE = (
    MyDialog, [
        (
            MyBadWidget, []
        ),
        (
            MyBadWidget, [
                (MyBadWidget, []),
                (MyBadWidget, [
                    (MyBadWidget, [
                        (MyBadWidget, []),
                        (MyBadWidget, []),
                    ])
                ]),
            ],
        ),
    ]
)


def create_content(widget_class, children_structures, parent=None):
    new_widget = QtGui.QWidget(parent=parent)
    layout = QtGui.QVBoxLayout(new_widget)
    layout.addWidget(widget_class())

    splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
    splitter.setStretchFactor(0, 2)
    layout.addWidget(splitter)

    children = []
    for child_class, substructures in children_structures:
        child, _ = create_content(child_class, substructures, parent=new_widget)
        children.append(child)
        splitter.addWidget(child)
    return new_widget, children


def create_structure(structure, parent_class=None):
    parent_class, substructures = structure
    return create_content(parent_class, substructures)


main = create_structure(STRUCTURE)
main.show()
toolkit().print_children(main)

main.deleteLater()
app.processEvents()
app.exec_()


# def dispose(widget):
#     print("Disposing ", widget)
#     widget.is_disposed.append(True)
#     widget.blockSignals(True)
#     widget.hide()
#     widget.setParent(None)
#     widget.deleteLater()


# nested_0, layout_0, _ = create_widget(n_widgets=3)
# nested_1, layout_1, inner_widget = create_widget(MyWidget, n_widgets=3, parent=nested_0)

# nested_0.show()

# # # Manually closing the entire dialog is okay!
# # app.exec_()
# # raise SystemExit(0)

# toolkit().print_children(nested_0)

# # nested_2.hide()
# # nested_2.deleteLater()

# toolkit().print_children(nested_0)

# # inner_widget represents a nested UI
# # This imitates a normal running condition where a nested UI is
# # disposed but not the rest.
# dispose(inner_widget)


# # # This raises
# # app.exec_()
# app.processEvents()
# #raise SystemExit(0)

# nested_0.blockSignals(True)
# nested_0.hide()
# nested_0.deleteLater()

# toolkit().print_children(nested_0)


# event_loop = QtCore.QEventLoop()

# def signal(obj):
#     print("Destroyed!", obj)
#     toolkit().print_children(obj)

# nested_0.destroyed.connect(event_loop.quit)
# nested_0.destroyed.connect(signal)

# event_loop.exec_()


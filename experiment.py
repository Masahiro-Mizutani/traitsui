from functools import partial

from pyface.qt import QtCore, QtGui
from traitsui.toolkit import toolkit


class MyBadWidget(QtGui.QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)

        # This list emulates shared mutable states on an editor
        # Hack: this gets set to an instance of FakeEditor
        # when we construct a structure.
        self.editor = None
        self.setText("Test")
        policy = self.sizePolicy()
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

    def sizeHint(self):
        print(f"{self} sizeHint is called")
        if self.editor.disposed:
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


def dispose_widget(widget):
    print(widget.editor)
    widget.editor.disposed = True
    widget.blockSignals(True)
    widget.hide()
    widget.deleteLater()


app = QtGui.QApplication([])


class FakeEditor:

    def __init__(self):
        self.disposed = False


editor1 = FakeEditor()
editor2 = FakeEditor()
editor3 = FakeEditor()
print(editor1, editor2, editor3)

STRUCTURE = (
    MyDialog, editor1, [
        (
            MyBadWidget, editor2, [],
        ),
        (
            MyBadWidget, editor3, [
                # All these widgets share the same editor.
                (MyBadWidget, None, []),
                (MyBadWidget, None, [
                    (MyBadWidget, None, [
                        (MyBadWidget, None, []),
                        (MyBadWidget, None, []),
                    ])
                ]),
            ],
        ),
    ]
)


def create_content(widget_class, children_structures, parent, editor):
    parent = QtGui.QWidget(parent=parent)
    layout = QtGui.QVBoxLayout(parent)

    new_widget = widget_class()
    new_widget.editor = editor

    if isinstance(new_widget, QtGui.QPushButton):
        new_widget.setText(repr(editor))
        new_widget.clicked.connect(partial(dispose_widget, new_widget))

    layout.addWidget(new_widget)

    splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
    splitter.setStretchFactor(0, 2)
    layout.addWidget(splitter)

    for child_class, new_editor, substructures in children_structures:
        child_editor = new_editor if new_editor is not None else editor
        child = create_content(
            child_class, substructures, parent=parent, editor=child_editor,
        )
        splitter.addWidget(child)
        child.setParent(splitter)
    return parent


def create_structure(structure, parent_class=None):
    parent_class, editor, substructures = structure
    return create_content(parent_class, substructures, parent=None, editor=editor)


main = create_structure(STRUCTURE)

main.show()
toolkit().print_children(main)

# main.hide()
# main.deleteLater()
# main.close()
# app.processEvents()
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


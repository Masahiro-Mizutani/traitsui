from functools import partial

from pyface.qt import QtCore, QtGui
from traitsui.toolkit import toolkit


class MyBadWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # This list emulates shared mutable states on an editor
        # Hack: this gets set to an instance of FakeEditor
        # when we construct a structure.
        self.editor = None
        self._inner = QtGui.QVBoxLayout()
        self.setLayout(self._inner)
        self._button = QtGui.QPushButton()
        self._button.setText("Close Editor")
        self._button.clicked.connect(self._dispose)
        self._inner.addWidget(self._button)

        # policy = self.sizePolicy()
        # policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        # policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        # self.setSizePolicy(policy)

    def _dispose(self):
        self.editor.dispose()

    def sizeHint(self):
        print(f"{self} sizeHint is called")
        if self.editor.disposed:
            raise RuntimeError("Uhoh")
        return super().sizeHint()

    def event(self, event):
        result = super().event(event)
        print(self, event, "hidden state: ", self.isHidden(), "visibility: ", self.isVisible())
        return result


class MyDialog(QtGui.QDialog):

    def closeEvent(self, event):
        print("Closing!")
        return super().closeEvent(event)

    def event(self, event):
        print(self, event)
        return super().event(event)


def _size_hint_wrapper(original_size_hint):

    def sizeHint():
        return original_size_hint()
    return sizeHint


app = QtGui.QApplication([])


class FakeEditor:

    def __init__(self):
        self.disposed = False
        self.main_widget = None

    def dispose(self):
        self.disposed = True
        if self.main_widget is not None:
            self.main_widget.hide()
            self.main_widget.deleteLater()
            self.main_widget = None


editor1 = FakeEditor()
editor2 = FakeEditor()
editor3 = FakeEditor()
editor4 = FakeEditor()
editors = [editor1, editor2, editor3, editor4]

STRUCTURE = (
    MyDialog, editor1, [
        (
            MyBadWidget, editor2, [],
        ),
        (
            MyBadWidget, editor3, [
                # All these widgets share the same editor.
                (MyBadWidget, None, []),
                (MyBadWidget, editor4, [
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
    new_widget.sizeHint = _size_hint_wrapper(new_widget.sizeHint)

    layout.addWidget(new_widget)

    splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
    splitter.setStretchFactor(0, 2)
    layout.addWidget(splitter)

    for child_class, new_editor, substructures in children_structures:
        child_editor = new_editor if new_editor is not None else editor
        child = create_content(
            child_class, substructures, parent=parent, editor=child_editor,
        )
        if new_editor is not None:
            new_editor.main_widget = child
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


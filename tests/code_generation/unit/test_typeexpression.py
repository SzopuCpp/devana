import unittest
from devana.code_generation.printers.default.basictypeprinter import BasicTypePrinter
from devana.code_generation.printers.default.typeexpressionprinter import TypeExpressionPrinter
from devana.code_generation.printers.default.typeexpressionprinter import GenericTypeParameterPrinter
from devana.code_generation.printers.default.unionprinter import UnionPrinter
from devana.code_generation.printers.default.typedefprinter import TypedefPrinter
from devana.code_generation.printers.default.enumprinter import EnumPrinter
from devana.code_generation.printers.default.classprinter import *
from devana.code_generation.printers.default.functiontypeprinter import FunctionTypePrinter
from devana.code_generation.printers.codeprinter import CodePrinter
from devana.syntax_abstraction.typeexpression import BasicType, TypeExpression, TypeModification
from devana.syntax_abstraction.classinfo import ClassInfo
from devana.syntax_abstraction.templateinfo import GenericTypeParameter
from devana.syntax_abstraction.typedefinfo import TypedefInfo
from devana.syntax_abstraction.unioninfo import UnionInfo
from devana.syntax_abstraction.enuminfo import EnumInfo
from devana.syntax_abstraction.functiontype import FunctionType


class TestTypeExpression(unittest.TestCase):

    def test_print_basic_type(self):
        cases = (
            ("int", BasicType.INT),
            ("unsigned int", BasicType.U_INT),
            ("short", BasicType.SHORT),
            ("unsigned short", BasicType.U_SHORT),
            ("char", BasicType.CHAR),
            ("unsigned char", BasicType.U_CHAR),
            ("long", BasicType.LONG),
            ("unsigned long", BasicType.U_LONG),
            ("long long", BasicType.LONG_LONG),
            ("unsigned long long", BasicType.U_LONG_LONG),
            ("bool", BasicType.BOOL),
            ("float", BasicType.FLOAT),
            ("double", BasicType.DOUBLE),
            ("long double", BasicType.LONG_DOUBLE),
            ("void", BasicType.VOID),
        )

        printer = BasicTypePrinter()
        for c in cases:
            with self.subTest(c[0]):
                result = printer.print(c[1])
                self.assertEqual(c[0], result)

    def test_print_type_expression_basic_mods_stand_alone(self):
        mods = (
            (TypeModification.CONST, "const double"),
            (TypeModification.REFERENCE, "double&"),
            (TypeModification.POINTER, "double*"),
            (TypeModification.STATIC, "static double"),
            (TypeModification.INLINE, "inline double"),
            (TypeModification.TEMPLATE, "template double"),
            (TypeModification.CONSTEXPR, "constexpr double"),
            (TypeModification.CONSTINIT, "constinit double"),
            (TypeModification.RESTRICT, "restrict double"),
            (TypeModification.VOLATILE, "volatile double"),
            (TypeModification.RVALUE_REF, "double&&"),
            (TypeModification.ARRAY, "double")
        )

        for m in mods:
            with self.subTest(m[0]):
                source = TypeExpression.create_default()
                source.details = BasicType.DOUBLE
                source.modification |= m[0]
                printer = TypeExpressionPrinter(BasicTypePrinter())
                result = printer.print(source)
                self.assertEqual(result, m[1])

    def test_print_type_expression_basic_mods_ptr_order(self):
        source = TypeExpression.create_default()
        source.details = BasicType.FLOAT
        source.modification |= TypeModification.create_pointer(3)
        printer = TypeExpressionPrinter(BasicTypePrinter())
        result = printer.print(source)
        self.assertEqual(result, "float***")

    def test_print_type_expression_basic_array(self):
        source = TypeExpression.create_default()
        source.details = BasicType.FLOAT
        source.modification |= TypeModification.create_array(["4", "8"])
        printer = TypeExpressionPrinter(BasicTypePrinter())
        result = printer.print(source)
        self.assertEqual(result, "float")


class TestTypeExpressionAdvanced(unittest.TestCase):

    def setUp(self):
        printer = CodePrinter()
        printer.register(BasicTypePrinter, BasicType)
        printer.register(TypeExpressionPrinter, TypeExpression)
        printer.register(ClassPrinter, ClassInfo)
        printer.register(GenericTypeParameterPrinter, GenericTypeParameter)
        printer.register(TypedefPrinter, TypedefInfo)
        printer.register(UnionPrinter, UnionInfo)
        printer.register(EnumPrinter, EnumInfo)
        printer.register(FunctionTypePrinter, FunctionType)
        self.printer: CodePrinter = printer

    def test_type_expression_class_details(self):
        class_type = ClassInfo.create_default()
        class_type.name = "TestClass"
        source = TypeExpression.create_default()
        source.details = class_type
        source.modification |= TypeModification.create_pointer(2)
        result = self.printer.print(source)
        self.assertEqual(result, "TestClass**")

    def test_type_expression_namespaces_class_details(self):
        class_type = ClassInfo.create_default()
        class_type.name = "TestClass"
        source = TypeExpression.create_default()
        source.details = class_type
        source.namespaces = ["Namespace1", "Namespace2"]
        result = self.printer.print(source)
        self.assertEqual(result, "Namespace1::Namespace2::TestClass")

    def test_type_expression_generic_type(self):
        generic_type = GenericTypeParameter("T")
        source = TypeExpression.create_default()
        source.details = generic_type
        source.modification |= TypeModification.CONST | TypeModification.POINTER
        result = self.printer.print(source)
        self.assertEqual(result, "const T*")

    def test_type_expression_template_basic_params(self):
        class_type = ClassInfo.create_default()
        class_type.name = "TestClass"
        source = TypeExpression.create_default()
        source.details = class_type

        param_1 = TypeExpression.create_default()
        param_1.modification |= TypeModification.POINTER
        param_1.details = BasicType.DOUBLE
        param_2 = TypeExpression.create_default()
        param_2.details = BasicType.U_CHAR
        param_3 = TypeExpression.create_default()
        param_3.modification = TypeModification.POINTER
        param_3.details = GenericTypeParameter("T")
        source.template_arguments = [param_1, param_2, param_3]
        result = self.printer.print(source)
        self.assertEqual(result, "TestClass<double*,unsigned char,T*>")

    def test_type_expression_template_class_param(self):
        class_type = ClassInfo.create_default()
        class_type.name = "TestClass"
        source = TypeExpression.create_default()
        source.details = class_type

        param_1 = TypeExpression.create_default()
        param_1.modification |= TypeModification.POINTER
        param_1.details = class_type
        source.template_arguments = [param_1]
        result = self.printer.print(source)
        self.assertEqual(result, "TestClass<TestClass*>")

    def test_type_expression_template_template_param(self):
        class_type = ClassInfo.create_default()
        class_type.name = "TestClass"
        source = TypeExpression.create_default()
        source.details = class_type

        param_1 = TypeExpression.create_default()
        param_1.modification |= TypeModification.POINTER
        param_1.details = class_type
        param_2 = TypeExpression.create_default()
        param_2.details = BasicType.INT
        param_1.template_arguments = [param_2]
        source.template_arguments = [param_1]

        result = self.printer.print(source)
        self.assertEqual(result, "TestClass<TestClass<int>*>")

    def test_type_expression_typedef_details(self):
        details_type = TypedefInfo.create_default()
        details_type.name = "TypedefTest"
        details_type.type_info = TypeExpression.create_default()
        details_type.type_info.details = BasicType.FLOAT
        source = TypeExpression.create_default()
        source.details = details_type
        source.modification |= TypeModification.POINTER
        result = self.printer.print(source)
        self.assertEqual(result, "TypedefTest*")

    def test_type_expression_union_details(self):
        details_type = UnionInfo.create_default()
        details_type.name = "TestUnion"
        source = TypeExpression.create_default()
        source.details = details_type
        source.modification |= TypeModification.POINTER
        result = self.printer.print(source)
        self.assertEqual(result, "TestUnion*")

    def test_type_expression_enum_details(self):
        details_type = EnumInfo.create_default()
        details_type.name = "TestEnum"
        source = TypeExpression.create_default()
        source.details = details_type
        source.modification |= TypeModification.POINTER
        result = self.printer.print(source)
        self.assertEqual(result, "TestEnum*")

    def test_type_expression_function_pointer_details(self):
        details_type = FunctionType.create_default()
        details_type.return_type = TypeExpression.create_default()
        details_type.return_type.details = BasicType.FLOAT
        details_type.arguments = [TypeExpression.create_default(), TypeExpression.create_default()]
        details_type.arguments[0].details = BasicType.DOUBLE
        details_type.arguments[0].modification |= TypeModification.POINTER
        details_type.arguments[1].details = BasicType.CHAR
        source = TypeExpression.create_default()
        source.details = details_type
        source.modification |= TypeModification.POINTER
        result = self.printer.print(source)
        self.assertEqual(result, "float (*)(double*, char)")

# -*- coding: utf-8 -*
__author__ = 'Trafimchuk Aliaksandr'

import idaapi
import idc


class MyHandler(idaapi.action_handler_t):
    @classmethod
    def get_name(self):
        return self.__name__
        
    @classmethod
    def get_label(self):
        return self.label
        
    @classmethod
    def register(self, plugin, label):
        self.plugin = plugin
        self.label = label
        instance = self()
        return idaapi.register_action(idaapi.action_desc_t(
            self.get_name(),  # Name. Acts as an ID. Must be unique.
            instance.get_label(),  # Label. That's what users see.
            instance  # Handler. Called when activated, and for updating
        ))

    @classmethod
    def unregister(self):
        """Unregister the action.
        After unregistering the class cannot be used.
        """
        idaapi.unregister_action(self.get_name())

    def activate(self, ctx):
        sel = idaapi.read_selection()
        if not sel[0]:
            print 'Please select something'
            return

        import capstone
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        md.details = True
        data = idaapi.get_many_bytes(sel[1], sel[2] - sel[1])
        for insn in md.disasm(data, sel[1]):
            # print "0x%x:\t%s\t%s" % (insn.address, insn.mnemonic, insn.op_str)
            idaapi.set_cmt(insn.address, str('%s %s' % (insn.mnemonic, insn.op_str)), False)

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS


class Hooks(idaapi.UI_Hooks):
    def finish_populating_tform_popup(self, form, popup):
        tft = idaapi.get_tform_type(form)

        if tft == idaapi.BWN_DISASM:
            # Define a silly handler.

            # Note the 'None' as action name (1st parameter).
            # That's because the action will be deleted immediately
            # after the context menu is hidden anyway, so there's
            # really no need giving it a valid ID.
            idaapi.attach_action_to_popup(form, popup, MyHandler.get_name(), "-")


class ida_embed_arch_disasm_t(idaapi.plugin_t):
    flags = idaapi.PLUGIN_KEEP
    comment = ""

    help = ""
    wanted_name = "IDA Embed ARCH Disasm as x86_64"
    wanted_hotkey = ""

    def __init__(self):
        super(ida_embed_arch_disasm_t, self).__init__()
        self._data = None
        self.hooks = None

    def init(self):
        MyHandler.register(self, self.wanted_name)
        self.hooks = Hooks()
        self.hooks.hook()
        return idaapi.PLUGIN_KEEP

    def run(self, arg):
        # refer to https://github.com/aquynh/capstone/blob/master/bindings/python/test_x86.py
        # [about actions in the menus] http://www.hexblog.com/?p=886
        pass

    def term(self):
        self._data = None
        self.hooks.unhook()
        self.hooks = None


# noinspection PyPep8Naming
def PLUGIN_ENTRY():
    return ida_embed_arch_disasm_t()

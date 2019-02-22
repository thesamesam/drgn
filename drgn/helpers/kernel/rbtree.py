# Copyright 2018 - Omar Sandoval
# SPDX-License-Identifier: GPL-3.0+

"""
Linux kernel red-black tree helpers

This module provides helpers for working with red-black trees from
"linux/rbtree.h"
"""

from drgn import container_of, Object, read_once


__all__ = [
    'RB_EMPTY_NODE',
    'rb_parent',
    'rb_first',
    'rb_last',
    'rb_next',
    'rb_prev',
    'rbtree_inorder_for_each',
    'rbtree_inorder_for_each_entry',
    'rb_find',
]


def RB_EMPTY_NODE(node):
    """
    bool RB_EMPTY_NODE(struct rb_node *)

    Return whether a red-black tree node is empty, i.e., not inserted in a
    tree.
    """
    return node.__rb_parent_color.value_() == node.value_()


def rb_parent(node):
    """
    struct rb_node *rb_parent(struct rb_node *)

    Return the parent node of a red-black tree node.
    """
    return Object(node.prog_, node.type_,
                  value=node.__rb_parent_color.value_() & ~3)


def rb_first(root):
    """
    struct rb_node *rb_first(struct rb_root *)

    Return the first node (in sort order) in a red-black tree, or a NULL object
    if the tree is empty.
    """
    node = read_once(root.rb_node)
    if not node:
        return node
    while True:
        next = read_once(node.rb_left)
        if not next:
            return node
        node = next


def rb_last(root):
    """
    struct rb_node *rb_last(struct rb_root *)

    Return the last node (in sort order) in a red-black tree, or a NULL object
    if the tree is empty.
    """
    node = read_once(root.rb_node)
    if not node:
        return node
    while True:
        next = read_once(node.rb_right)
        if not next:
            return node
        node = next


def rb_next(node):
    """
    struct rb_node *rb_next(struct rb_node *)

    Return the next node (in sort order) after a red-black node, or a NULL
    object if the node is the last node in the tree or is empty.
    """
    node = read_once(node)

    if RB_EMPTY_NODE(node):
        return NULL(node.prog_, node.type_)

    next = read_once(node.rb_right)
    if next:
        node = next
        while True:
            next = read_once(node.rb_left)
            if not next:
                return node
            node = next

    parent = read_once(rb_parent(node))
    while parent and node == parent.rb_right:
        node = parent
        parent = read_once(rb_parent(node))
    return parent


def rb_prev(node):
    """
    struct rb_node *rb_prev(struct rb_node *)

    Return the previous node (in sort order) before a red-black node, or a NULL
    object if the node is the first node in the tree or is empty.
    """
    node = read_once(node)

    if RB_EMPTY_NODE(node):
        return NULL(node.prog_, node.type_)

    next = read_once(node.rb_left)
    if next:
        node = next
        while True:
            next = read_once(node.rb_right)
            if not next:
                return node
            node = next

    parent = read_once(rb_parent(node))
    while parent and node == parent.rb_left:
        node = parent
        parent = read_once(rb_parent(node))
    return parent


def rbtree_inorder_for_each(root):
    """
    rbtree_inorder_for_each(struct rb_root *)

    Return an iterator over all of the nodes in a red-black tree, in sort
    order.
    """
    def aux(node):
        if node:
            yield from aux(read_once(node.rb_left))
            yield node
            yield from aux(read_once(node.rb_right))
    yield from aux(read_once(root.rb_node))


def rbtree_inorder_for_each_entry(type, root, member):
    """
    rbtree_inorder_for_each_entry(type, struct rb_root *, member)

    Return an iterator over all of the entries in a red-black tree, given the
    type of the entry and the struct list_head member in that type. The entries
    are returned in sort order.
    """
    for node in rbtree_inorder_for_each(root):
        yield container_of(node, type, member)


def rb_find(type, root, member, key, cmp):
    """
    type *rb_find(type, struct rb_root *, member,
                  key_type key, int (*cmp)(key_type, type *))

    Find an entry in a red-black tree, given a key and a comparator function
    which takes the key and an entry. The comparator should return -1 if the
    key is less than the entry, 1 if it is greater than the entry, or 0 if it
    matches the entry. This returns a NULL object if no entry matches the key.

    Note that this function does not have an analogue in the Linux kernel
    source code, as tree searches are all open-coded.
    """
    node = read_once(root.rb_node)
    while node:
        entry = container_of(node, type, member)
        ret = cmp(key, entry)
        if ret < 0:
            node = read_once(node.rb_left)
        elif ret > 0:
            node = read_once(node.rb_right)
        else:
            return entry
    return node

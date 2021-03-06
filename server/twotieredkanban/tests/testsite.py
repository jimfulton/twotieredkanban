import unittest
from testvars import Vars
import ZODB
from ZODB.utils import u64

from .sample import users

class SiteTests(unittest.TestCase):

    def setUp(self):
        from ..site import Site
        self.site = Site("Test")
        self.generation = self.site.generation
        self.conn = ZODB.connection(None)
        self.conn.root.site = self.site
        self.conn.transaction_manager.commit()

    def updates(self):
        updates = self.site.updates(self.generation)
        self.generation = updates.pop('generation')
        return updates

    def test_new_site(self):
        self.assertEqual(self.site.title, "Test")
        self.assertEqual(self.site.users, ())
        self.assertEqual(dict(self.site.boards), {})
        self.assertEqual(self.site, self.site.updates(0)['site'])

    def test_add_board(self):
        vars = Vars()
        generation = self.site.generation
        self.site.add_board('first', 'The first one', 'Yup, the first')
        self.assertEqual([('first', vars.board)],
                         list(self.site.boards.items()))
        self.assertEqual(self.site, vars.board.site)
        self.assertEqual('first', vars.board.name)
        self.assertEqual('The first one', vars.board.title)
        self.assertEqual('Yup, the first', vars.board.description)
        self.assertTrue(self.site.generation > generation)

        generation = vars.board.generation
        self.site.add_board('second', 'The second one', 'Yup, the second')
        self.assertEqual(['first', 'second'], list(self.site.boards))

        # The original board was updated:
        self.assertTrue(vars.board.generation > generation)

    def test_rename_board(self):
        self.site.add_board('first', '', '')
        board = self.site.boards['first']
        board_generation = board.generation
        self.updates()

        # renaming to same name is a noop:
        self.site.rename('first', 'first')
        self.assertEqual({}, self.updates())
        self.assertEqual(board_generation, board.generation)

        self.site.rename('first', 'fist')
        self.assertEqual(self.site, self.updates()['site'])
        self.assertEqual([dict(name='fist', title='', description='')],
                         self.site.json_reduce()['boards'])
        self.assertEqual(board, board.updates(board_generation)['board'])
        self.assertEqual('fist', board.name)

    def test_update_users(self):
        self.site.add_board('first', 'The first one', 'Yup, the first')
        board = self.site.boards['first']
        site_generation = self.site.generation
        board_generation = board.generation
        self.site.update_users(users)
        self.assertEqual(list(users), self.site.users)
        self.assertTrue(self.site.generation > site_generation)
        self.assertTrue(board.generation > board_generation)

    def test_json(self):
        self.site.add_board('first', 'The first one', 'Yup, the first')
        self.site.update_users(users)
        self.assertEqual(
            dict(users=list(users),
                 boards=[dict(name='first',
                              title='The first one',
                              description='Yup, the first')]),
            self.site.json_reduce(),
            )

    def test_site_updates(self):
        self.site.add_board('first', 'The first one', 'Yup, the first')
        self.site.update_users(users)

        self.assertEqual(
            {'generation': Vars().x,
             'site': self.site, 'zoid': str(u64(self.site.changes._p_oid))},
            self.site.updates(0))

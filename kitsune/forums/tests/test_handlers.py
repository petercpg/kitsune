from kitsune.forums.handlers import PostListener, ThreadListener
from kitsune.forums.models import Thread
from kitsune.forums.tests import PostFactory, ThreadFactory
from kitsune.sumo.tests import TestCase
from kitsune.users.models import Profile
from kitsune.users.tests import UserFactory


class TestThreadListener(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.sumo_bot = Profile.get_sumo_bot()
        self.listener = ThreadListener()

    def test_multiple_threads_reassignment(self):
        """Test that multiple threads are reassigned correctly."""
        thread1 = ThreadFactory(creator=self.user)
        PostFactory(thread=thread1)

        thread2 = ThreadFactory(creator=self.user)
        PostFactory(thread=thread2)

        thread3 = ThreadFactory(creator=self.user)
        PostFactory(thread=thread3)

        self.listener.on_user_deletion(self.user)

        for thread in [thread1, thread2, thread3]:
            thread.refresh_from_db()
            self.assertEqual(thread.creator.username, self.sumo_bot.username)

    def test_other_users_threads_unaffected(self):
        """Test that other users' threads are not affected."""
        other_user = UserFactory()
        thread1 = ThreadFactory(creator=self.user)
        PostFactory(thread=thread1)
        thread2 = ThreadFactory(creator=other_user)
        PostFactory(thread=thread2)

        self.listener.on_user_deletion(self.user)

        thread1.refresh_from_db()
        thread2.refresh_from_db()
        self.assertEqual(thread1.creator.username, self.sumo_bot.username)
        self.assertEqual(thread2.creator, other_user)

    def test_empty_thread_deletion(self):
        """Test that threads with no replies are deleted."""
        empty_thread = ThreadFactory(creator=self.user)
        thread_with_replies = ThreadFactory(creator=self.user)
        PostFactory(thread=thread_with_replies)

        self.listener.on_user_deletion(self.user)

        with self.assertRaises(Thread.DoesNotExist):
            empty_thread.refresh_from_db()

        thread_with_replies.refresh_from_db()
        self.assertEqual(thread_with_replies.creator.username, self.sumo_bot.username)


class TestPostListener(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.sumo_bot = Profile.get_sumo_bot()
        self.listener = PostListener()

    def test_multiple_posts_reassignment(self):
        """Test that multiple posts are reassigned correctly."""
        post1 = PostFactory(author=self.user)
        post2 = PostFactory(author=self.user)
        post3 = PostFactory(author=self.user)

        self.listener.on_user_deletion(self.user)

        for post in [post1, post2, post3]:
            post.refresh_from_db()
            self.assertEqual(post.author.username, self.sumo_bot.username)

    def test_other_users_posts_unaffected(self):
        """Test that other users' posts are not affected."""
        other_user = UserFactory()
        post1 = PostFactory(author=self.user)
        post2 = PostFactory(author=other_user)

        self.listener.on_user_deletion(self.user)

        post1.refresh_from_db()
        post2.refresh_from_db()
        self.assertEqual(post1.author.username, self.sumo_bot.username)
        self.assertEqual(post2.author, other_user)

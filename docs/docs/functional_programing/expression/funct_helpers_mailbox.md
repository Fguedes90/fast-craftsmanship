Mailbox
class AsyncReplyChannel(fn: Callable[[_Reply], None])

class MailboxProcessor(cancellation_token: CancellationToken | None)

post(msg: _Msg) → None

    Post a message synchronously to the mailbox processor.

    This method is not asynchronous since it’s very fast to execute. It simply adds the message to the message queue of the mailbox processor and returns.

    Parameters:

        msg – Message to post.
    Returns:

        None

post_and_async_reply(build_message: Callable[[AsyncReplyChannel[_Reply]], _Msg]) → Awaitable[_Reply]

    Post with async reply.

    Post a message asynchronously to the mailbox processor and wait for the reply.

    Parameters:

            build_message – A function that takes a reply channel

            send ((AsyncReplyChannel[Reply]) and returns a message to)

            the (to the mailbox processor. The message should contain)

            tuple. (reply channel as e.g a)

    Returns:

        The reply from mailbox processor.

async receive() → _Msg

    Receive message from mailbox.

    Returns:

        An asynchronous computation which will consume the first message in arrival order. No thread is blocked while waiting for further messages. Raises a TimeoutException if the timeout is exceeded.


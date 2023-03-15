import textwrap
import traceback

from discord import Interaction
from discord.message import Message
from enum import Enum
from objection_engine.beans.comment import Comment
from typing import List, Optional


class State(Enum):
    QUEUED = 0
    INPROGRESS = 1
    FAILED = 2
    RENDERED = 3
    UPLOADING = 4
    DONE = 5


class Render:
    def __init__(
        self,
        state: State,
        feedbackMessage: Message,
        messages: List[Comment],
        music: str,
        discordInteraction: Optional[Interaction] = None,
        discordReply: Optional[Message] = None,
    ):
        self.state = state
        self.discordInteraction = discordInteraction
        self.discordReply = discordReply
        self.feedbackMessage = feedbackMessage
        self.messages = messages
        self.outputFilename = f"{str(self.get_id())}.mp4"
        self.music_code = music

    def getStateString(self):
        if self.state == State.QUEUED:
            return "Queued"
        if self.state == State.INPROGRESS:
            return "In progress"
        if self.state == State.FAILED:
            return "Failed"
        if self.state == State.RENDERED:
            return "Rendered"
        if self.state == State.UPLOADING:
            return "Uploading"
        if self.state == State.DONE:
            return "Done"

    def getState(self):
        return self.state

    def getInteraction(self):
        return self.discordInteraction

    def getFeedbackMessage(self):
        return self.feedbackMessage

    def getMessages(self):
        return self.messages

    def getOutputFilename(self):
        return self.outputFilename

    def setState(self, state: State):
        self.state = state

    async def reply(self, **kwargs):
        if self.discordInteraction is not None:
            return await self.discordInteraction.followup.send(**kwargs)
        else:
            return await self.discordReply.reply(**kwargs)

    async def edit(self, **kwargs):
        if self.discordInteraction is not None:
            return await self.discordInteraction.followup.edit(**kwargs)
        else:
            return await self.discordReply.edit(**kwargs)

    def get_guild_id(self):
        if self.discordInteraction is not None:
            return self.discordInteraction.guild_id
        else:
            return self.discordReply.guild.id

    def get_user_id(self):
        if self.discordInteraction is not None:
            return self.discordInteraction.user.id
        else:
            return self.discordReply.author.id

    def get_id(self):
        if self.discordInteraction is not None:
            return self.discordInteraction.id
        else:
            return self.discordReply.id

    async def updateFeedback(self, newContent: str):
        try:
            newContent = textwrap.dedent(newContent).strip("\n")
            # Feedback messages will only be updated if their content is different to the new Content, to avoid spamming Discord's API
            if self.feedbackMessage.content != newContent:
                await self.edit(content=newContent)
            # If it's unable to edit/get the feedback message, it will raise an exception and that means that it no longer exists
        except Exception as exception:
            # If it doesn't exist, we will repost it.
            traceback.print_exc()
            print(f"Error: {exception}")
            self.feedbackMessage = await self.reply(content=newContent)

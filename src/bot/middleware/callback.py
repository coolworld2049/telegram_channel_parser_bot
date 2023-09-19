from typing import Any, Awaitable, Callable, Dict, Optional, Union

from aiogram import BaseMiddleware, loggers
from aiogram.dispatcher.flags import get_flag
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import CallbackQuery, TelegramObject
from aiogram.utils.callback_answer import CallbackAnswer


class CallbackAnswerMiddleware(BaseMiddleware):
    def __init__(
        self,
        pre: bool = False,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
    ) -> None:
        """
        Inner middleware for callback query handlers, can be useful in bots with a lot of callback
        handlers to automatically take answer to all requests

        :param pre: send answer before execute handler
        :param text: answer with text
        :param show_alert: show alert
        :param url: game url
        :param cache_time: cache answer for some time
        """
        self.pre = pre
        self.text = text
        self.show_alert = show_alert
        self.url = url
        self.cache_time = cache_time

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)

        callback_answer = data["callback_answer"] = self.construct_callback_answer(
            properties=get_flag(data, "callback_answer")
        )

        if not callback_answer.disabled and callback_answer.answered:
            try:
                await self.answer(event, callback_answer)
            except:
                pass
        try:
            return await handler(event, data)
        finally:
            if not callback_answer.disabled and not callback_answer.answered:
                try:
                    await self.answer(event, callback_answer)
                except:
                    pass

    def construct_callback_answer(
        self, properties: Optional[Union[Dict[str, Any], bool]]
    ) -> CallbackAnswer:
        pre, disabled, text, show_alert, url, cache_time = (
            self.pre,
            False,
            self.text,
            self.show_alert,
            self.url,
            self.cache_time,
        )
        if isinstance(properties, dict):
            pre = properties.get("pre", pre)
            disabled = properties.get("disabled", disabled)
            text = properties.get("text", text)
            show_alert = properties.get("show_alert", show_alert)
            url = properties.get("url", url)
            cache_time = properties.get("cache_time", cache_time)

        return CallbackAnswer(
            answered=pre,
            disabled=disabled,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time,
        )

    def answer(
        self, event: CallbackQuery, callback_answer: CallbackAnswer
    ) -> AnswerCallbackQuery:
        loggers.middlewares.info("Answer to callback query id=%s", event.id)
        return event.answer(
            text=callback_answer.text,
            show_alert=callback_answer.show_alert,
            url=callback_answer.url,
            cache_time=callback_answer.cache_time,
        )

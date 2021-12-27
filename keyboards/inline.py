from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_like_btn = InlineKeyboardButton("0", callback_data='like')
inline_dislike_btn = InlineKeyboardButton("0", callback_data='dislike')
like_kb = InlineKeyboardMarkup().add(inline_like_btn, inline_dislike_btn)


def update_btn(text: str, btn: str):
    if btn == 'like':
        inline_like_btn.text = f'{text}👍'
    elif btn == 'dislike':
        inline_dislike_btn.text = f'{text}👎🏿'


def set_btn(likes, dislikes):
    inline_like_btn.text = f'{likes}👍'
    inline_dislike_btn.text = f'{dislikes}👎🏿'

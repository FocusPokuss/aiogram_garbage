from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


PHOTOS_ON_PAGE = 8


def get_photo_rating_kb(data, photo_id):
    return InlineKeyboardMarkup().add(InlineKeyboardButton(f'{data[0]}👍', callback_data=f'actionlike_{photo_id}'),
                                      InlineKeyboardButton(f'{data[1]}👎🏿', callback_data=f'actiondislike_{photo_id}'))


def get_photos_kb(photos, page=0):
    photo_buttons = [InlineKeyboardButton(title, callback_data=f'photo_{photo_id}')
                     for title, photo_id in photos[page*PHOTOS_ON_PAGE:page*PHOTOS_ON_PAGE + PHOTOS_ON_PAGE]]
    switch_buttons = []
    if page == 0:
        switch_buttons.append(InlineKeyboardButton('>', callback_data=f'page_{page+1}'))
    elif page == len(photos) // PHOTOS_ON_PAGE:  # if page is last
        switch_buttons.append(InlineKeyboardButton('<', callback_data=f'page_{page-1}'))
    else:
        switch_buttons.extend([InlineKeyboardButton('<', callback_data=f'page_{page-1}'),
                               InlineKeyboardButton('>', callback_data=f'page_{page+1}')])

    return InlineKeyboardMarkup(row_width=4).add(*photo_buttons).row(*switch_buttons).\
        row(InlineKeyboardButton(f'Выйти', callback_data='exit_from_photos'))

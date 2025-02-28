from modules.discord.views import PaginatedCardView, PaginatedViewStyle, ButtonColor


class ActivitySummaryView(PaginatedCardView):
    def __init__(self, activity):
        cards = []

        style = PaginatedViewStyle()
        style.to_beginning_button_color = ButtonColor.GREEN
        style.to_end_button_color = ButtonColor.GREEN
        style.previous_button_color = ButtonColor.BLURPLE
        style.next_button_color = ButtonColor.BLURPLE

        super().__init__(cards=cards, title="Current Activity", style=style)

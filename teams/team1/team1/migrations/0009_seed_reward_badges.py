from django.db import migrations


def seed_rewards(apps, schema_editor):
    """
    Fixes a real bug: distribute_rewards() (called automatically from
    calculate_final_rankings) looks up Reward rows by badge_type with
    .get(), but nothing ever created them on a fresh database — so the
    very first challenge to close would crash with Reward.DoesNotExist.

    get_or_create keeps this migration safe to re-run.
    """
    Reward = apps.get_model("team1", "Reward")

    badges = [
        ("top1", "Awarded to the #1 ranked participant in a challenge."),
        ("top3", "Awarded to participants ranked in the top 3 of a challenge."),
        ("top10", "Awarded to participants ranked in the top 10 of a challenge."),
    ]

    for badge_type, description in badges:
        Reward.objects.get_or_create(
            badge_type=badge_type,
            defaults={"description": description},
        )


def unseed_rewards(apps, schema_editor):
    Reward = apps.get_model("team1", "Reward")
    Reward.objects.filter(badge_type__in=["top1", "top3", "top10"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("team1", "0008_reward_userbadge"),
    ]

    operations = [
        migrations.RunPython(seed_rewards, reverse_code=unseed_rewards),
    ]
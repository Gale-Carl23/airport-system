from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create and configure BOC-NAIA system roles"

    def handle(self, *args, **options):

        roles = {
            "Administrator": {
                "passenger": ["view", "add", "change", "delete"],
                "flight": ["view", "add", "change", "delete"],
                "baggage": ["view", "add", "change", "delete"],
                "inspection": ["view", "add", "change", "delete"],
                "assessment": ["view", "add", "change", "delete"],
                "payment": ["view", "add", "change", "delete"],
                "clearance": ["view", "add", "change", "delete"],
                "case": ["view", "add", "change", "delete"],
                "auditlog": ["view"],
            },

            "Customs Examiner": {
                "passenger": ["view", "add", "change"],
                "flight": ["view"],
                "baggage": ["view", "add", "change"],
                "inspection": ["view", "add", "change"],
            },

            "Assessment Officer": {
                "passenger": ["view"],
                "flight": ["view"],
                "baggage": ["view"],
                "inspection": ["view"],
                "assessment": ["view", "add", "change"],
            },

            "Cashier": {
                "passenger": ["view"],
                "flight": ["view"],
                "baggage": ["view"],
                "inspection": ["view"],
                "assessment": ["view"],
                "payment": ["view", "add", "change"],
            },

            "Enforcement Officer": {
                "passenger": ["view"],
                "flight": ["view"],
                "baggage": ["view"],
                "inspection": ["view"],
                "case": ["view", "add", "change"],
            },

            "Clearance Officer": {
                "passenger": ["view"],
                "flight": ["view"],
                "baggage": ["view"],
                "inspection": ["view"],
                "assessment": ["view"],
                "payment": ["view"],
                "clearance": ["view", "add", "change"],
            },
        }

        for role_name, model_permissions in roles.items():

            group, created = Group.objects.get_or_create(
                name=role_name
            )

            group.permissions.clear()

            for model_name, actions in model_permissions.items():

                for action in actions:

                    codename = f"{action}_{model_name}"

                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type__app_label="passengers",
                        )

                        group.permissions.add(permission)

                    except Permission.DoesNotExist:

                        self.stdout.write(
                            self.style.WARNING(
                                f"Permission not found: {codename}"
                            )
                        )

            group.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created role: {role_name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated role: {role_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "BOC-NAIA roles and permissions configured successfully."
            )
        )
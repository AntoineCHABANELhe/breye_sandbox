from colorama import Fore


class Migration:
    models = [
        "Activity",
        "Action",
        "ErrorLog",
        "User",
        "Session",
        "Occurrence",
        "Analyse",
        "ResponseToken",
        "ResponseWord",
        "ResponseBlock",
        "LastSent",
        "Setting"
    ]

    def __init__(self):
        pass

    def print(self, text, **kwargs):
        print(Fore.BLUE + "[Migration] >>", Fore.RESET + text, **kwargs)

    def load(self):
        for model in Migration.models:
            try:
                self.print(f"    loading {Fore.CYAN}{model:14}{Fore.RESET}", end=" ")
                module = __import__(f"Source.Database.Models.{model}", fromlist=["Model"])
                model_class = getattr(module, model)
                model_class().migrate()
            except Exception as e:            
                self.print(f"\n    {model} failed to load.")                
                print(e)

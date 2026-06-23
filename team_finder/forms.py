from .validators import validate_github_url


def clean_github_url(github_url):
    if not github_url:
        return github_url
    validate_github_url(github_url)
    return github_url


class GithubUrlCleanMixin:
    def clean_github_url(self):
        return clean_github_url(self.cleaned_data.get("github_url"))

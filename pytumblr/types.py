from collections import UserList
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Type

DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'


def parse_date(tumblr_date: str) -> datetime:
    return datetime.strptime(tumblr_date, DATE_FORMAT)


@dataclass
class Link:
    """
    An objects in a _links hash
    """
    href: str
    type: str


@dataclass
class NavigationLink(Link):
    pass


@dataclass
class ActionLink(Link):
    method: str
    query_params: Dict[str, Any]


_link_classes = {'navigation': NavigationLink,
                 'action': ActionLink}


@dataclass
class Tag:
    tag: str
    is_tracked: bool
    featured: bool
    thumb_url: Optional[str] = None


@dataclass
class BaseBlog:
    name: str
    updated: int
    title: str
    description: str


@dataclass
class Blog(BaseBlog):
    url: str


@dataclass
class BlogInfo(BaseBlog):
    posts: int
    ask: bool
    ask_anon: bool
    likes: int
    is_blocked_from_primary: bool


@dataclass
class UserBlogInfo:
    url: str
    title: str
    primary: bool
    followers: int
    tweet: str
    facebook: str
    type: str


@dataclass
class UserInfo:
    following: int
    default_post_format: str
    name: str
    likes: int
    blogs: List[UserBlogInfo]

    def __post_init__(self):
        self.blogs = [UserBlogInfo(**blog) for blog in self.blogs]


@dataclass
class Avatar:
    avatar_url: str


@dataclass
class Post:
    id: int
    type: str
    blog_name: str
    post_url: str
    timestamp: int
    date: datetime
    format: str
    reblog_key: str
    tags: List[str]
    total_posts: int

    blog: Optional[BlogInfo] = None

    bookmarks: Optional[bool] = None
    mobile: Optional[bool] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    liked: Optional[bool] = None
    state: Optional[str] = None
    is_blocks_post_format: Optional[bool] = None

    def __new__(cls, *args, **kwargs):
        if 'blog_name' in kwargs and 'blog' not in kwargs:
            return DashboardPost(*args, **kwargs)
        else:
            return POST_CLASSES[kwargs['type']](*args, **kwargs)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __post_init__(self):
        self.date = parse_date(self.date)
        self.blog = BlogInfo(**self.blog)


@dataclass
class DashboardPost(Post):
    blog: None = None


@dataclass
class Submission(Post):
    slug: str = None
    short_url: str = None

    post_author: Optional[str] = None
    is_submission: Optional[bool] = True
    anonymous_name: Optional[str] = None
    anonymous_email: Optional[str] = None
    state: Optional[str] = 'submission'


@dataclass
class LegacyTextPost(Post):
    title: Optional[str] = None
    body: Optional[str] = None


@dataclass
class ImageSize:
    width: int
    height: int
    url: str


@dataclass
class Photo:
    caption: str
    alt_sizes: List[ImageSize]

    def __post_init__(self):
        self.alt_sizes = [ImageSize(**size) for size in self.alt_sizes]


@dataclass
class VerbosePhoto(Photo):
    original_size: ImageSize
    width: int
    height: int
    url: str

    def __post_init__(self):
        self.original_size = ImageSize(**self.original_size)


@dataclass
class LegacyPhotoPost(Post):
    """
    A photo or photoset post
    """
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    photos: List[Photo] = field(default_factory=list)

    def __post_init__(self):
        self.photos = [Photo(**photo) for photo in self.photos]


@dataclass
class LegacyQuotePost(Post):
    text: Optional[str] = None
    # HTML source, not an attribution
    source: Optional[str] = None


@dataclass
class LegacyLinkPost(Post):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    excerpt: Optional[str] = None
    publisher: Optional[str] = None
    photos: List[VerbosePhoto] = field(default_factory=list)

    def __post_init__(self):
        self.photos = [VerbosePhoto(**photo) for photo in self.photos]


@dataclass
class ChatLine:
    name: str
    label: str
    phrase: str


@dataclass
class LegacyChatPost(Post):
    title: Optional[str] = None
    body: Optional[str] = None
    dialogue: List[ChatLine] = field(default_factory=list)

    def __post_init__(self):
        self.dialogue = [ChatLine(**line) for line in self.dialogue]


@dataclass
class LegacyAudioPost(Post):
    caption: Optional[str] = None
    player: Optional[str] = None
    plays: Optional[int] = None
    album_art: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    track_name: Optional[str] = None
    track_number: Optional[int] = None
    year: Optional[int] = None


@dataclass
class VideoPlayer:
    width: int
    embed_code: str


@dataclass
class LegacyVideoPost(Post):
    caption: Optional[str] = None
    player: List[Any] = field(default_factory=[])


@dataclass
class LegacyAnswerPost(Post):
    asking_name: Optional[str] = None
    asking_url: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None


# a type -> class dict
POST_CLASSES: Dict[str, Type] = {
    'photo': LegacyPhotoPost,
    'quote': LegacyQuotePost,
    'link': LegacyLinkPost,
    'chat': LegacyChatPost,
    'audio': LegacyAudioPost,
    'video': LegacyVideoPost,
    'answer': LegacyAnswerPost,
}

@dataclass
class Likes:
    liked_posts: List[Post]
    liked_count: int

    def __post_init__(self):
        self.liked_posts = [Post(**post) for post in self.liked_posts]


@dataclass
class Following:
    blogs: List[BlogInfo]
    total_blogs: int

    def __post_init__(self):
        self.blogs = [BlogInfo(**blog) for blog in self.blogs]


@dataclass
class Follower:
    name: str
    following: bool
    url: str
    updated: int


@dataclass
class Followers:
    total_users: int
    users: List[Follower]

    def __post_init__(self):
        self.users = [Follower(**user) for user in self.users]


@dataclass
class Reblog:
    comment: str
    tree_html: str


@dataclass
class Dashboard:
    posts: List[DashboardPost]

    def __post_init__(self):
        self.posts = [DashboardPost(**post) for post in self.posts]


@dataclass
class Posts:
    posts: List[Post]

    def __post_init__(self):
        self.posts = [Post(**post) for post in self.posts]


@dataclass
class BlogPosts(Posts):
    blog: BlogInfo

    def __post_init__(self):
        self.blog = BlogInfo(**self.blog)

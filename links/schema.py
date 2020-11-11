import graphene
from graphene_django import DjangoObjectType
from links.models import Link, Vote
from django.db.models import Q


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType):
    links = graphene.List(LinkType, search=graphene.String())
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, **kwargs):
        if search:
            filter = (
                    Q(url__icontaions=search) |
                    Q(description_icontains=search)
            )
            return Link.objects.filter(filter)
        return Link.objects.all()

    def resolve_votes(self, info):
        return Vote.objects.all()


class CreateLink(graphene.Mutation):
    link = graphene.Field(LinkType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user
        link = Link.objects.create(url=url, description=description, posted_by=user)
        return CreateLink(
            link=link
        )


class CreateVote(graphene.Mutation):
    vote = graphene.Field(VoteType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('you must log in to vote')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception("Invalid link")

        vote = Vote.objects.create(
            user=user,
            link=link
        )
        return CreateVote(
            vote=vote
        )


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()

import graphene
from graphene_django import DjangoObjectType
from links.models import Link


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class Query(graphene.ObjectType):
    links = graphene.List(LinkType)

    def resolve_links(self, info):
        return Link.objects.all()


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


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()

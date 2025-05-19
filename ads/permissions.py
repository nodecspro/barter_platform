# ads/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the ad.
        return obj.user == request.user


class IsProposalOwnerOrReceiver(permissions.BasePermission):
    """
    Custom permission for ExchangeProposal.
    - Proposer can view.
    - Receiver's ad owner can view and update status.
    - Proposer can potentially delete/cancel if status is pending.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return obj.proposer == request.user or obj.ad_receiver.user == request.user

        # For PUT, PATCH (updating status)
        if request.method in ["PUT", "PATCH"]:
            # Only the owner of the ad_receiver can change the status typically
            return obj.ad_receiver.user == request.user

        # For DELETE (cancelling)
        if request.method == "DELETE":
            # Proposer can cancel if pending, or receiver can "delete" (treat as reject)
            return (obj.proposer == request.user and obj.status == "pending") or (
                obj.ad_receiver.user == request.user
            )  # Receiver can "delete" a proposal made to them

        return False


class IsReceiverOfAdForProposal(permissions.BasePermission):
    """
    Permission to check if the current user is the owner of the ad_receiver
    for an ExchangeProposal. Used for actions like accept/reject.
    """

    def has_object_permission(self, request, view, obj):
        return obj.ad_receiver.user == request.user

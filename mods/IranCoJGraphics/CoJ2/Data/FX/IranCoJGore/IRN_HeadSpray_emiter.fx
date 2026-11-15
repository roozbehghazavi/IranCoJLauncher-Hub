EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.4)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 12, 16)
	}

	StartVelocity()
	{
		keyf(0, 450)
	}

	StartVelocityRand()
	{
		keyv(0, 200, 260, 200)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(0.6)
	}
}

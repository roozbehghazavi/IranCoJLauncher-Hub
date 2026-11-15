EmiterDef()
{
	LifeTime()
	{
		keyf(0, 2.2)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 2)
	}

	StartVelocity()
	{
		keyf(0, 320)
	}

	StartVelocityRand()
	{
		keyv(0, 120, 120, 120)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
